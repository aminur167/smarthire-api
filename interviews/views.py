"""Views for the interviews app."""

from django.utils import timezone
from rest_framework import viewsets, generics, permissions
from accounts.permissions import IsAdminOrRecruiter
from .models import Interview
from .serializers import InterviewSerializer, InterviewCreateSerializer


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
            return qs.filter(interviewer=user)
        return qs.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return InterviewCreateSerializer
        return InterviewSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminOrRecruiter()]
        return [permissions.IsAuthenticated()]


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
            return qs.filter(interviewer=user)
        return qs
