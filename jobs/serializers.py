"""Serializers for the jobs app."""

from rest_framework import serializers
from accounts.serializers import UserProfileSerializer
from .models import Department, JobPosting


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description", "created_at"]


class JobPostingSerializer(serializers.ModelSerializer):
    """Full representation with nested relations."""

    department_detail = DepartmentSerializer(source="department", read_only=True)
    posted_by_detail = UserProfileSerializer(source="posted_by", read_only=True)
    time_to_hire_days = serializers.ReadOnlyField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            "id", "title", "department", "department_detail",
            "description", "requirements", "responsibilities",
            "location", "job_type", "experience_level",
            "salary_min", "salary_max", "openings", "closed_count",
            "deadline", "status", "skills_required",
            "posted_by", "posted_by_detail", "time_to_hire_days",
            "application_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "posted_by", "closed_count", "created_at", "updated_at"]

    def get_application_count(self, obj):
        return obj.applications.count() if hasattr(obj, "applications") else 0


class JobPostingCreateSerializer(serializers.ModelSerializer):
    """Slim serializer for creating / updating a job posting."""

    class Meta:
        model = JobPosting
        fields = [
            "title", "department", "description", "requirements",
            "responsibilities", "location", "job_type", "experience_level",
            "salary_min", "salary_max", "openings", "deadline",
            "status", "skills_required",
        ]

    def create(self, validated_data):
        validated_data["posted_by"] = self.context["request"].user
        return super().create(validated_data)
