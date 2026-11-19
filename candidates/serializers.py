"""Serializers for the candidates app."""

from rest_framework import serializers
from django.utils import timezone
from accounts.serializers import UserProfileSerializer
from jobs.serializers import JobPostingSerializer
from .models import CandidateProfile, Application


class CandidateProfileSerializer(serializers.ModelSerializer):
    user_detail = UserProfileSerializer(source="user", read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            "id", "user", "user_detail", "resume", "parsed_data", "skills",
            "experience_years", "education", "current_company", "current_position",
            "expected_salary", "linkedin_url", "portfolio_url", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "parsed_data", "created_at", "updated_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_detail = UserProfileSerializer(source="candidate", read_only=True)
    job_detail = JobPostingSerializer(source="job", read_only=True)
    match_scoring_available = serializers.SerializerMethodField()

    def get_match_scoring_available(self, obj):
        return bool(obj.job.skills_required)

    class Meta:
        model = Application
        fields = [
            "id", "candidate", "candidate_detail", "job", "job_detail",
            "status", "cover_letter", "ai_match_score", "match_scoring_available", "notes",
            "applied_at", "updated_at",
        ]
        read_only_fields = ["id", "candidate", "ai_match_score", "applied_at", "updated_at"]


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["job", "cover_letter"]

    def validate_job(self, value):
        if value.status != "PUBLISHED":
            raise serializers.ValidationError("This job is not currently accepting applications.")
        if value.deadline < timezone.localdate():
            raise serializers.ValidationError("The application deadline for this job has passed.")
        if value.closed_count >= value.openings:
            raise serializers.ValidationError("All openings for this job have been filled.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if Application.objects.filter(candidate=user, job=attrs["job"]).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return attrs

    def create(self, validated_data):
        validated_data["candidate"] = self.context["request"].user
        return super().create(validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status", "notes"]
