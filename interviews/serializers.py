"""Serializers for the interviews app."""

from rest_framework import serializers
from django.utils import timezone
from accounts.models import User
from accounts.serializers import UserProfileSerializer
from candidates.serializers import ApplicationSerializer
from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    interviewer_detail = UserProfileSerializer(source="interviewer", read_only=True)
    application_detail = ApplicationSerializer(source="application", read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id", "application", "application_detail",
            "interviewer", "interviewer_detail",
            "scheduled_at", "duration_minutes", "interview_type",
            "status", "meeting_link", "location",
            "notes", "feedback", "rating",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class InterviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            "application", "interviewer", "scheduled_at",
            "duration_minutes", "interview_type", "meeting_link", "location",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        application = attrs.get("application", getattr(self.instance, "application", None))
        interviewer = attrs.get("interviewer", getattr(self.instance, "interviewer", None))
        if request and request.user.role == User.Role.RECRUITER:
            if application and application.job.posted_by_id != request.user.id:
                raise serializers.ValidationError({"application": "Choose an application from one of your job postings."})
            if interviewer and interviewer.id != request.user.id:
                raise serializers.ValidationError({"interviewer": "You can only schedule interviews under your account."})
        if request and request.user.role == User.Role.ADMIN and interviewer and interviewer.role != User.Role.ADMIN:
            if not interviewer.is_staff and interviewer.role != User.Role.RECRUITER:
                raise serializers.ValidationError({"interviewer": "Choose an administrator or recruiter as the interviewer."})
        scheduled_at = attrs.get("scheduled_at", getattr(self.instance, "scheduled_at", None))
        if scheduled_at and scheduled_at <= timezone.now() and self.instance is None:
            raise serializers.ValidationError({"scheduled_at": "Choose a future time for the interview."})
        if attrs.get("duration_minutes", getattr(self.instance, "duration_minutes", 60)) < 15:
            raise serializers.ValidationError({"duration_minutes": "An interview must be at least 15 minutes."})
        return attrs


class InterviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ["status", "meeting_link", "location", "notes", "feedback", "rating"]

    def validate_rating(self, value):
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
