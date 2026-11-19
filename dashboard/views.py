"""Dashboard aggregate views."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from accounts.permissions import IsAdmin, IsAdminOrRecruiter, IsCandidate
from ai_engine.matcher import explain_match

from candidates.models import Application
from jobs.models import JobPosting
from interviews.models import Interview

User = get_user_model()


class DashboardStatsView(APIView):
    """Application status counts for the dashboard cards."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        apps = Application.objects.all()
        jobs = JobPosting.objects.all()
        interviews = Interview.objects.all()
        if request.user.role == "RECRUITER":
            jobs = jobs.filter(posted_by=request.user)
            apps = apps.filter(job__posted_by=request.user)
            interviews = interviews.filter(application__job__posted_by=request.user)
        elif request.user.role == "CANDIDATE":
            apps = apps.filter(candidate=request.user)
            jobs = JobPosting.objects.filter(status=JobPosting.Status.PUBLISHED)
            interviews = interviews.filter(application__candidate=request.user)
        data = {
            "new_applications": apps.filter(status="NEW").count(),
            "screening": apps.filter(status="SCREENING").count(),
            "qualified": apps.filter(status="QUALIFIED").count(),
            "scheduled": apps.filter(status="INTERVIEW_SCHEDULED").count(),
            "interviewed": apps.filter(status="INTERVIEWED").count(),
            "offered": apps.filter(status="OFFERED").count(),
            "joined": apps.filter(status="HIRED").count(),
            "rejected": apps.filter(status="REJECTED").count(),
            "total": apps.count(),
            "total_applications": apps.count(),
            "total_jobs": jobs.count(),
            "active_jobs": jobs.filter(status=JobPosting.Status.PUBLISHED).count(),
            "total_candidates": apps.values("candidate_id").distinct().count(),
            "total_interviews": interviews.count(),
        }
        return Response(data)


class JobsOverviewView(APIView):
    """Jobs overview for the dashboard table."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jobs = JobPosting.objects.select_related("department").filter(status__in=["PUBLISHED", "ON_HOLD"])
        if request.user.role == "RECRUITER":
            jobs = jobs.filter(posted_by=request.user)
        elif request.user.role == "CANDIDATE":
            jobs = jobs.filter(status=JobPosting.Status.PUBLISHED, deadline__gte=timezone.localdate())
        jobs = jobs[:10]
        data = []
        for job in jobs:
            delta = (job.updated_at - job.created_at).days if job.closed_count else None
            data.append({
                "id": job.id,
                "title": job.title,
                "department": job.department.name if job.department else "—",
                "deadline": job.deadline,
                "status": job.status,
                "openings": job.openings,
                "closed": job.closed_count,
                "time_to_hire": f"{delta} days" if delta else "—",
                "application_count": job.applications.count(),
            })
        return Response(data)


class RequestsSummaryView(APIView):
    """Hiring request summary for the sidebar cards."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jobs = JobPosting.objects.all()
        if request.user.role == "RECRUITER":
            jobs = jobs.filter(posted_by=request.user)
        elif request.user.role == "CANDIDATE":
            jobs = jobs.filter(status=JobPosting.Status.PUBLISHED, deadline__gte=timezone.localdate())
        published = jobs.filter(status="PUBLISHED").count()
        draft = jobs.filter(status="DRAFT").count()
        on_hold = jobs.filter(status="ON_HOLD").count()
        closed = jobs.filter(status="CLOSED").count()
        data = {
            "single_hiring": published,
            "modify_hiring": draft,
            "assign_recruiter": on_hold,
            "referral_bonus": closed,
            "total": published + draft + on_hold + closed,
        }
        return Response(data)


class RecentActivityView(APIView):
    """Recent activity feed."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        recent_apps = Application.objects.select_related("candidate", "job").order_by("-applied_at")
        recent_interviews = Interview.objects.select_related(
            "application__candidate", "application__job"
        ).order_by("-created_at")
        if request.user.role == "RECRUITER":
            recent_apps = recent_apps.filter(job__posted_by=request.user)
            recent_interviews = recent_interviews.filter(application__job__posted_by=request.user)
        elif request.user.role == "CANDIDATE":
            recent_apps = recent_apps.filter(candidate=request.user)
            recent_interviews = recent_interviews.filter(application__candidate=request.user)
        recent_apps = recent_apps[:10]
        recent_interviews = recent_interviews[:10]

        activities = []
        for app in recent_apps:
            activities.append({
                "type": "application",
                "message": f"{app.candidate.get_full_name()} applied for {app.job.title}",
                "status": app.status,
                "timestamp": app.applied_at.isoformat(),
            })
        for interview in recent_interviews:
            activities.append({
                "type": "interview",
                "message": f"Interview scheduled for {interview.application.candidate.get_full_name()}",
                "status": interview.status,
                "timestamp": interview.created_at.isoformat(),
            })

        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return Response(activities[:20])


class ReportsView(APIView):
    """Hiring analytics derived from persisted applications and job records."""

    permission_classes = [IsAdminOrRecruiter]

    def get(self, request):
        try:
            months = int(request.query_params.get("months", 6))
        except (TypeError, ValueError):
            months = 6
        months = min(max(months, 3), 12)
        today = timezone.localdate()
        first_month = today.month - months + 1
        first_year = today.year + (first_month - 1) // 12
        first_month = (first_month - 1) % 12 + 1
        start_date = datetime(first_year, first_month, 1).date()

        applications = Application.objects.select_related("job", "job__department")
        jobs = JobPosting.objects.all()
        if request.user.role == "RECRUITER":
            applications = applications.filter(job__posted_by=request.user)
            jobs = jobs.filter(posted_by=request.user)

        status_counts = {status: 0 for status, _label in Application.Status.choices}
        for row in applications.values("status").annotate(count=Count("id")):
            status_counts[row["status"]] = row["count"]

        grouped_months = {
            row["month"].strftime("%Y-%m"): row["count"]
            for row in applications.filter(applied_at__date__gte=start_date)
            .annotate(month=TruncMonth("applied_at"))
            .values("month")
            .annotate(count=Count("id"))
        }
        monthly = []
        for offset in range(months):
            index = today.year * 12 + today.month - 1 - (months - offset - 1)
            date = datetime(index // 12, index % 12 + 1, 1)
            key = date.strftime("%Y-%m")
            monthly.append({"month": date.strftime("%b"), "applications": grouped_months.get(key, 0)})

        department_rows = applications.values("job__department__name").annotate(
            applications=Count("id")
        ).order_by("-applications")[:8]
        departments = [
            {"department": row["job__department__name"] or "Unassigned", "applications": row["applications"]}
            for row in department_rows
        ]
        top_jobs = list(jobs.annotate(
            applications=Count("applications"),
            hires=Count("applications", filter=Q(applications__status=Application.Status.HIRED)),
        ).values("id", "title", "applications", "hires").order_by("-applications", "title")[:8])

        total = sum(status_counts.values())
        hires = status_counts[Application.Status.HIRED]
        rejected = status_counts[Application.Status.REJECTED]
        return Response({
            "period_months": months,
            "summary": {
                "applications": total,
                "hires": hires,
                "active_jobs": jobs.filter(status=JobPosting.Status.PUBLISHED).count(),
                "in_review": total - hires - rejected,
                "hire_rate": round(hires * 100 / total, 1) if total else 0,
            },
            "status_counts": status_counts,
            "monthly_applications": monthly,
            "applications_by_department": departments,
            "top_jobs": top_jobs,
        })


class AdminStatsView(APIView):
    """Platform-wide administration statistics and telemetry."""

    permission_classes = [IsAdmin]

    def get(self, request):
        total_users = User.objects.count()
        admins = User.objects.filter(role="ADMIN").count()
        recruiters = User.objects.filter(role="RECRUITER").count()
        candidates = User.objects.filter(role="CANDIDATE").count()

        total_jobs = JobPosting.objects.count()
        active_jobs = JobPosting.objects.filter(status="PUBLISHED").count()
        total_apps = Application.objects.count()
        total_interviews = Interview.objects.count()

        recent_users = User.objects.order_by("-date_joined")[:10]
        users_data = [
            {
                "id": u.id,
                "full_name": u.get_full_name() or u.email.split("@")[0],
                "email": u.email,
                "role": u.role,
                "is_verified": u.is_verified,
                "date_joined": u.date_joined.strftime("%Y-%m-%d"),
            }
            for u in recent_users
        ]

        return Response({
            "users": {
                "total": total_users,
                "admins": admins,
                "recruiters": recruiters,
                "candidates": candidates,
            },
            "platform": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "total_applications": total_apps,
                "total_interviews": total_interviews,
            },
            "recent_users": users_data,
        })


class CandidatePortalView(APIView):
    """Candidate-specific dashboard: applications, status pipeline, and recommended jobs."""

    permission_classes = [IsCandidate]

    def get(self, request):
        user = request.user
        apps = Application.objects.select_related("job", "job__department").filter(candidate=user).order_by("-applied_at")
        my_apps = [
            {
                "id": a.id,
                "job_id": a.job.id,
                "job_title": a.job.title,
                "department": a.job.department.name if a.job.department else "General",
                "location": a.job.location,
                "job_type": a.job.job_type,
                "status": a.status,
                "match_score": a.ai_match_score,
                "applied_at": a.applied_at.strftime("%b %d, %Y"),
            }
            for a in apps
        ]

        profile = getattr(user, "candidate_profile", None)
        candidate_skills = profile.skills if profile else []
        candidate_jobs = []
        for job in JobPosting.objects.filter(
            status=JobPosting.Status.PUBLISHED,
            deadline__gte=timezone.localdate(),
        ).exclude(
            applications__candidate=user
        ).select_related("department").distinct():
            match = explain_match(candidate_skills, job.skills_required)
            candidate_jobs.append({
                "id": job.id,
                "title": job.title,
                "department": job.department.name if job.department else "General",
                "location": job.location,
                "job_type": job.job_type,
                "salary_min": str(job.salary_min) if job.salary_min is not None else None,
                "salary_max": str(job.salary_max) if job.salary_max is not None else None,
                "skills": job.skills_required or [],
                "openings": job.openings,
                "match_score": match["score"],
                "match_scoring_available": match["scoring_available"],
                "matched_skills": match["matched_skills"],
                "missing_skills": match["missing_skills"],
            })
        recommended = sorted(candidate_jobs, key=lambda job: job["match_score"], reverse=True)[:6]

        upcoming_interviews = Interview.objects.select_related("application__job", "interviewer").filter(
            application__candidate=user,
            status__in=["SCHEDULED", "RESCHEDULED"],
            scheduled_at__gte=timezone.now(),
        ).order_by("scheduled_at")
        interview_count = upcoming_interviews.count()
        interviews = upcoming_interviews[:5]

        my_interviews = [
            {
                "id": i.id,
                "job_title": i.application.job.title,
                "scheduled_at": i.scheduled_at.strftime("%b %d, %Y • %I:%M %p"),
                "round_type": i.interview_type,
                "meeting_link": i.meeting_link,
                "interviewer_name": i.interviewer.get_full_name() if i.interviewer else "Hiring Team",
                "status": i.status,
            }
            for i in interviews
        ]

        return Response({
            "my_applications": my_apps,
            "total_applied": len(my_apps),
            "interviews_count": interview_count,
            "recommended_jobs": recommended,
            "upcoming_interviews": my_interviews,
            "has_resume": bool(profile and profile.resume),
            "profile": {
                "skills": profile.skills,
                "experience_years": profile.experience_years,
                "education": profile.education,
                "current_company": profile.current_company,
                "current_position": profile.current_position,
            } if profile else None,
        })
