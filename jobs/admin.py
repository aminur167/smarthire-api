"""Admin configuration for jobs."""

from django.contrib import admin
from .models import Department, JobPosting


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "status", "job_type", "openings", "closed_count", "deadline", "created_at")
    list_filter = ("status", "job_type", "experience_level", "department")
    search_fields = ("title", "description", "location")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
