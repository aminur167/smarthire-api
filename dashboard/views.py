"""Dashboard aggregate views."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from candidates.models import Application
from jobs.models import JobPosting
from interviews.models import Interview


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
