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
from ai_engine.matcher import calculate_match_score


class CandidateProfileViewSet(viewsets.ModelViewSet):
    """Manage candidate profiles."""

    serializer_class = CandidateProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("ADMIN", "RECRUITER"):
            return CandidateProfile.objects.select_related("user").all()
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
        parsed = parse_resume_file(profile.resume.path)
        profile.parsed_data = parsed
        profile.skills = parsed.get("skills", [])
        profile.experience_years = parsed.get("experience_years", 0)
        if parsed.get("linkedin"):
            profile.linkedin_url = parsed["linkedin"]
        profile.save()

        return Response({
            "message": "Resume uploaded and parsed successfully.",
            "parsed_data": parsed,
            "profile": CandidateProfileSerializer(profile).data,
        })


class ApplicationViewSet(viewsets.ModelViewSet):
    """Manage job applications."""

    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        if self.action in ("update", "partial_update"):
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("ADMIN", "RECRUITER"):
            return Application.objects.select_related("candidate", "job", "job__department").all()
        return Application.objects.filter(candidate=user).select_related("job", "job__department")

    def get_permissions(self):
        if self.action == "create":
            return [IsCandidate()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminOrRecruiter()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        application = serializer.save()
        # Calculate AI match score
        try:
            profile = CandidateProfile.objects.get(user=application.candidate)
            score = calculate_match_score(profile.skills, application.job.skills_required)
            application.ai_match_score = score
            application.save(update_fields=["ai_match_score"])
        except CandidateProfile.DoesNotExist:
            pass
