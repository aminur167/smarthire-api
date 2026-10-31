"""Filters for the jobs app."""

import django_filters
from .models import JobPosting


class JobPostingFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    max_salary = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")
    deadline_after = django_filters.DateFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = django_filters.DateFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = JobPosting
        fields = ["status", "job_type", "experience_level", "department", "location"]
