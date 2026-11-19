"""Views for the interviews app."""

from django.utils import timezone
from rest_framework import viewsets, generics, permissions
from accounts.permissions import IsAdminOrRecruiter
from .models import Interview
from .serializers import InterviewSerializer, InterviewCreateSerializer, InterviewUpdateSerializer
from notifications.models import Notification
from candidates.models import Application


class InterviewViewSet(viewsets.ModelViewSet):
    """CRUD for interviews."""

    def get_queryset(self):
        user = self.request.user
        qs = Interview.objects.select_related(
            "application__candidate", "application__job", "interviewer"
        )
        if user.role == "CANDIDATE":
            return qs.filter(application__candidate=user)
        if user.role == "RECRUITER":
            return qs.filter(application__job__posted_by=user)
        return qs.all()

    def get_serializer_class(self):
        if self.action == "create":
            return InterviewCreateSerializer
        if self.action in ("update", "partial_update"):
            return InterviewUpdateSerializer
        return InterviewSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminOrRecruiter()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        interview = serializer.save()
        application = interview.application
        if application.status not in (Application.Status.HIRED, Application.Status.REJECTED):
            application.status = Application.Status.INTERVIEW_SCHEDULED
            application.save(update_fields=["status", "updated_at"])
        Notification.objects.create(
            user=application.candidate,
            title="Interview scheduled",
            message=f"A {interview.get_interview_type_display().lower()} interview for {application.job.title} is scheduled for {interview.scheduled_at:%b %d, %Y at %I:%M %p}.",
            notification_type=Notification.NotificationType.INTERVIEW,
            link="/interviews",
        )

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        interview = serializer.save()
        if interview.status != old_status:
            Notification.objects.create(
                user=interview.application.candidate,
                title="Interview updated",
                message=f"The interview for {interview.application.job.title} is now {interview.get_status_display().lower()}.",
                notification_type=Notification.NotificationType.INTERVIEW,
                link="/interviews",
            )


class UpcomingInterviewsView(generics.ListAPIView):
    """List upcoming interviews for the authenticated user."""

    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        qs = Interview.objects.filter(
            scheduled_at__gte=now,
            status=Interview.Status.SCHEDULED,
        ).select_related("application__candidate", "application__job", "interviewer")

        if user.role == "CANDIDATE":
            return qs.filter(application__candidate=user)
        if user.role == "RECRUITER":
            return qs.filter(application__job__posted_by=user)
        return qs
