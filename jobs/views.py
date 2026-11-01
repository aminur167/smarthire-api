"""Views for the jobs app."""

from rest_framework import viewsets, permissions
from accounts.permissions import IsAdminOrRecruiter
from .models import Department, JobPosting
from .serializers import DepartmentSerializer, JobPostingSerializer, JobPostingCreateSerializer
from .filters import JobPostingFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    """CRUD for departments."""

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.IsAuthenticated()]
        return [IsAdminOrRecruiter()]


class JobPostingViewSet(viewsets.ModelViewSet):
    """CRUD for job postings with filtering, search, and ordering."""

    queryset = JobPosting.objects.select_related("department", "posted_by").all()
    filterset_class = JobPostingFilter
    search_fields = ["title", "description", "location", "skills_required"]
    ordering_fields = ["created_at", "deadline", "salary_min", "title"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return JobPostingCreateSerializer
        return JobPostingSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrRecruiter()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Non-staff see only published jobs
        if not self.request.user.is_authenticated or self.request.user.role == "CANDIDATE":
            qs = qs.filter(status=JobPosting.Status.PUBLISHED)
        return qs
