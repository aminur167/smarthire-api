"""Celery tasks for SmartHire background processing."""

from smarthire.celery_app import app


@app.task(name="tasks.parse_resume")
def parse_resume_task(profile_id: int):
    """Parse a candidate's uploaded resume in the background."""
    from candidates.models import CandidateProfile
    from candidates.resume_parser import parse_resume_file

    try:
        profile = CandidateProfile.objects.get(pk=profile_id)
        if not profile.resume:
            return {"error": "No resume uploaded"}

        parsed = parse_resume_file(profile.resume.path)
        profile.parsed_data = parsed
        profile.skills = parsed.get("skills", [])
        profile.experience_years = parsed.get("experience_years", 0)
        profile.save(update_fields=["parsed_data", "skills", "experience_years"])
        return {"status": "success", "profile_id": profile_id}
    except CandidateProfile.DoesNotExist:
        return {"error": f"Profile {profile_id} not found"}


@app.task(name="tasks.calculate_match_scores")
def calculate_match_scores_task(job_id: int):
    """Recalculate AI match scores for all applications of a job."""
    from candidates.models import Application, CandidateProfile
    from jobs.models import JobPosting
    from ai_engine.matcher import calculate_match_score

    try:
        job = JobPosting.objects.get(pk=job_id)
    except JobPosting.DoesNotExist:
        return {"error": f"Job {job_id} not found"}

    applications = Application.objects.filter(job=job)
    updated = 0

    for app_obj in applications:
        try:
            profile = CandidateProfile.objects.get(user=app_obj.candidate)
            score = calculate_match_score(profile.skills, job.skills_required)
            app_obj.ai_match_score = score
            app_obj.save(update_fields=["ai_match_score"])
            updated += 1
        except CandidateProfile.DoesNotExist:
            continue

    return {"status": "success", "job_id": job_id, "updated": updated}


@app.task(name="tasks.send_interview_reminder")
def send_interview_reminder_task():
    """Create reminder notifications for interviews happening in the next 24 hours."""
    from django.utils import timezone
    from datetime import timedelta
    from interviews.models import Interview
    from notifications.models import Notification

    now = timezone.now()
    upcoming = Interview.objects.filter(
        scheduled_at__gte=now,
        scheduled_at__lte=now + timedelta(hours=24),
        status=Interview.Status.SCHEDULED,
    ).select_related("application__candidate", "application__job", "interviewer")

    created = 0
    for interview in upcoming:
        job_title = interview.application.job.title
        time_str = interview.scheduled_at.strftime("%I:%M %p")

        # Notify candidate
        Notification.objects.get_or_create(
            user=interview.application.candidate,
            title="Interview Reminder",
            message=f"Your interview for {job_title} is at {time_str} tomorrow.",
            notification_type="INTERVIEW",
        )
        # Notify interviewer
        Notification.objects.get_or_create(
            user=interview.interviewer,
            title="Interview Reminder",
            message=f"You have an interview for {job_title} at {time_str} tomorrow.",
            notification_type="INTERVIEW",
        )
        created += 2

    return {"status": "success", "reminders_created": created}
