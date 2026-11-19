"""Views for the candidates app."""

from rest_framework import viewsets, generics, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsAdminOrRecruiter, IsCandidate

from .models import CandidateProfile, Application
from .serializers import (
    CandidateProfileSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
)
from .resume_parser import parse_resume_file
from ai_engine.matcher import calculate_match_score, explain_match
from notifications.models import Notification


class CandidateProfileViewSet(viewsets.ModelViewSet):
    """Manage candidate profiles."""

    serializer_class = CandidateProfileSerializer
    search_fields = ["user__first_name", "user__last_name", "user__email", "current_position", "current_company"]
    ordering_fields = ["experience_years", "updated_at", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ("ADMIN", "RECRUITER"):
            profiles = CandidateProfile.objects.select_related("user").all()
            if user.role == "RECRUITER":
                profiles = profiles.filter(user__applications__job__posted_by=user).distinct()
            return profiles
        return CandidateProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResumeUploadView(APIView):
    """Upload a PDF resume, parse it, and update the candidate profile."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        resume_file = request.FILES.get("resume")
        if not resume_file:
            return Response({"error": "No resume file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not resume_file.name.lower().endswith(".pdf"):
            return Response({"error": "Only PDF files are accepted."}, status=status.HTTP_400_BAD_REQUEST)

        if resume_file.size > 10 * 1024 * 1024:
            return Response({"error": "File size must be under 10 MB."}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        profile.resume = resume_file
        profile.save()

        # Parse the uploaded resume
        try:
            parsed = parse_resume_file(profile.resume.path)
        except Exception:
            parsed = {"error": "We could not read this PDF. Try exporting it again and re-uploading.", "skills": [], "experience_years": 0}
        profile.parsed_data = parsed
        if not parsed.get("error"):
            profile.skills = parsed.get("skills", [])
            profile.experience_years = parsed.get("experience_years", 0)
            if parsed.get("linkedin"):
                profile.linkedin_url = parsed["linkedin"]
        profile.save()

        if not parsed.get("error"):
            for application in profile.user.applications.select_related("job"):
                application.ai_match_score = calculate_match_score(profile.skills, application.job.skills_required)
                application.save(update_fields=["ai_match_score"])

        return Response({
            "message": "Resume uploaded and parsed successfully." if not parsed.get("error") else "Resume uploaded, but automatic text extraction needs a manual profile review.",
            "parse_status": "complete" if not parsed.get("error") else "needs_review",
            "parsed_data": parsed,
            "profile": CandidateProfileSerializer(profile).data,
        })


class ApplicationViewSet(viewsets.ModelViewSet):
    """Manage job applications."""

    filterset_fields = ["status", "job"]
    search_fields = ["candidate__first_name", "candidate__last_name", "candidate__email", "job__title"]
    ordering_fields = ["applied_at", "updated_at", "ai_match_score", "status"]

    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        if self.action in ("update", "partial_update"):
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("ADMIN", "RECRUITER"):
            applications = Application.objects.select_related("candidate", "job", "job__department").all()
            if user.role == "RECRUITER":
                applications = applications.filter(job__posted_by=user)
            return applications
        return Application.objects.filter(candidate=user).select_related("job", "job__department")

    def get_permissions(self):
        if self.action == "create":
            return [IsCandidate()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminOrRecruiter()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        application = serializer.save()
        profile, _ = CandidateProfile.objects.get_or_create(user=application.candidate)
        application.ai_match_score = calculate_match_score(profile.skills, application.job.skills_required)
        application.save(update_fields=["ai_match_score"])

    def perform_update(self, serializer):
        previous_status = serializer.instance.status
        application = serializer.save()
        if application.status != previous_status:
            Notification.objects.create(
                user=application.candidate,
                title="Application status updated",
                message=f"Your application for {application.job.title} moved to {application.get_status_display()}.",
                notification_type=Notification.NotificationType.APPLICATION,
                link="/applications",
            )


class ApplicationMatchView(APIView):
    """Explain the skill-coverage score for an application without making a hiring decision."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, application_id):
        try:
            application = Application.objects.select_related("candidate", "job").get(pk=application_id)
        except Application.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_admin = user.role == "ADMIN"
        is_candidate_owner = user.role == "CANDIDATE" and application.candidate_id == user.id
        is_job_recruiter = user.role == "RECRUITER" and application.job.posted_by_id == user.id
        if not (is_admin or is_candidate_owner or is_job_recruiter):
            return Response({"detail": "You do not have access to this application."}, status=status.HTTP_403_FORBIDDEN)

        profile = getattr(application.candidate, "candidate_profile", None)
        candidate_skills = profile.skills if profile else []
        explanation = explain_match(candidate_skills, application.job.skills_required)
        return Response({
            **explanation,
            "method": "required_skill_coverage",
            "human_review_required": True,
            "note": "This score compares listed skills only. Review the resume and application before making a decision.",
        })
