"""Admin configuration for interviews."""

from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "interviewer", "interview_type", "status", "scheduled_at", "rating")
    list_filter = ("status", "interview_type")
    search_fields = ("application__candidate__email", "application__job__title", "interviewer__email")
    date_hierarchy = "scheduled_at"
    readonly_fields = ("created_at", "updated_at")
