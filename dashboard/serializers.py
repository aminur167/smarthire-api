"""Dashboard serializers."""

from rest_framework import serializers


class ApplicationStatsSerializer(serializers.Serializer):
    new_applications = serializers.IntegerField()
    qualified = serializers.IntegerField()
    scheduled = serializers.IntegerField()
    interviewed = serializers.IntegerField()
    joined = serializers.IntegerField()
    total = serializers.IntegerField()


class JobOverviewItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    department = serializers.CharField()
    deadline = serializers.DateField()
    status = serializers.CharField()
    openings = serializers.IntegerField()
    closed = serializers.IntegerField()
    time_to_hire = serializers.CharField(allow_null=True)


class RequestSummarySerializer(serializers.Serializer):
    single_hiring = serializers.IntegerField()
    modify_hiring = serializers.IntegerField()
    assign_recruiter = serializers.IntegerField()
    referral_bonus = serializers.IntegerField()
    total = serializers.IntegerField()
