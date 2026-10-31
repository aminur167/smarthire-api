"""Models for the jobs app."""

from django.conf import settings
from django.db import models


class Department(models.Model):
    """Company department / team."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    """A single job opening."""

    class JobType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"
        REMOTE = "REMOTE", "Remote"
        INTERNSHIP = "INTERNSHIP", "Internship"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "ENTRY", "Entry Level"
        MID = "MID", "Mid Level"
        SENIOR = "SENIOR", "Senior Level"
        LEAD = "LEAD", "Lead / Manager"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ON_HOLD = "ON_HOLD", "On Hold"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="jobs")
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    openings = models.PositiveIntegerField(default=1)
    closed_count = models.PositiveIntegerField(default=0)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    skills_required = models.JSONField(default=list, blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"

    def __str__(self):
        return f"{self.title} – {self.department}"

    @property
    def time_to_hire_days(self):
        """Average days from open to first close (placeholder calculation)."""
        if self.closed_count > 0:
            delta = self.updated_at - self.created_at
            return delta.days
        return None

    @property
    def is_active(self):
        return self.status == self.Status.PUBLISHED
