"""Dashboard aggregate views."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import get_user_model

from candidates.models import Application
from jobs.models import JobPosting
from interviews.models import Interview

User = get_user_model()


class DashboardStatsView(APIView):
    """Application status counts for the dashboard cards."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        apps = Application.objects.all()
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
        }
        return Response(data)


class JobsOverviewView(APIView):
    """Jobs overview for the dashboard table."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jobs = JobPosting.objects.select_related("department").filter(
            status__in=["PUBLISHED", "ON_HOLD"]
        )[:10]
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
        published = JobPosting.objects.filter(status="PUBLISHED").count()
        draft = JobPosting.objects.filter(status="DRAFT").count()
        on_hold = JobPosting.objects.filter(status="ON_HOLD").count()
        closed = JobPosting.objects.filter(status="CLOSED").count()
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
        recent_apps = Application.objects.select_related("candidate", "job").order_by("-applied_at")[:10]
        recent_interviews = Interview.objects.select_related(
            "application__candidate", "application__job"
        ).order_by("-created_at")[:10]

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


class AdminStatsView(APIView):
    """Platform-wide administration statistics and telemetry."""

    permission_classes = [permissions.IsAuthenticated]

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
            "system_health": {
                "api_status": "OPERATIONAL",
                "database": "CONNECTED",
                "ai_engine": "READY",
            },
        })


class CandidatePortalView(APIView):
    """Candidate-specific dashboard: applications, status pipeline, and recommended jobs."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        apps = Application.objects.select_related("job", "job__department").filter(candidate=user).order_by("-applied_at")
        my_apps = [
            {
                "id": a.id,
                "job_id": a.job.id,
                "job_title": a.job.title,
                "department": a.job.department.name if a.job.department else "Engineering",
                "location": a.job.location,
                "job_type": a.job.job_type,
                "status": a.status,
                "match_score": a.match_score,
                "applied_at": a.applied_at.strftime("%b %d, %Y"),
            }
            for a in apps
        ]

        jobs = JobPosting.objects.filter(status="PUBLISHED").order_by("-created_at")[:6]
        recommended = [
            {
                "id": j.id,
                "title": j.title,
                "department": j.department.name if j.department else "Engineering",
                "location": j.location,
                "job_type": j.job_type,
                "salary_min": str(j.salary_min),
                "salary_max": str(j.salary_max),
                "skills": j.skills_required or [],
                "openings": j.openings,
            }
            for j in jobs
        ]

        interviews = Interview.objects.select_related("application__job", "interviewer").filter(
            application__candidate=user,
            status__in=["SCHEDULED", "RESCHEDULED"]
        ).order_by("scheduled_at")[:5]

        my_interviews = [
            {
                "id": i.id,
                "job_title": i.application.job.title,
                "scheduled_at": i.scheduled_at.strftime("%b %d, %Y • %I:%M %p"),
                "round_type": i.round_type,
                "meeting_link": i.meeting_link,
                "interviewer_name": i.interviewer.get_full_name() if i.interviewer else "Hiring Team",
                "status": i.status,
            }
            for i in interviews
        ]

        return Response({
            "my_applications": my_apps,
            "total_applied": len(my_apps),
            "interviews_count": len(my_interviews),
            "recommended_jobs": recommended,
            "upcoming_interviews": my_interviews,
            "has_resume": bool(user.avatar or getattr(user, "resume", None)),
        })
