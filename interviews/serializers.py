"""Serializers for the interviews app."""

from rest_framework import serializers
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
