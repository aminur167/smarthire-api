"""Admin configuration for candidates."""

from django.contrib import admin
from .models import CandidateProfile, Application


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "experience_years", "current_company", "current_position", "created_at")
    search_fields = ("user__email", "user__first_name", "current_company")
    list_filter = ("experience_years",)
    readonly_fields = ("parsed_data", "created_at", "updated_at")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "ai_match_score", "applied_at")
    list_filter = ("status",)
    search_fields = ("candidate__email", "job__title")
    date_hierarchy = "applied_at"
    readonly_fields = ("ai_match_score", "applied_at", "updated_at")
