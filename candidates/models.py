"""Models for the candidates app."""

from django.conf import settings
from django.db import models


class CandidateProfile(models.Model):
    """Extended profile for candidates with resume data."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    education = models.TextField(blank=True)
    current_company = models.CharField(max_length=200, blank=True)
    current_position = models.CharField(max_length=200, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Candidate Profile"

    def __str__(self):
        return f"Profile: {self.user.email}"


class Application(models.Model):
    """A candidate's application to a specific job posting."""

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        SCREENING = "SCREENING", "Screening"
        QUALIFIED = "QUALIFIED", "Qualified"
        INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED", "Interview Scheduled"
        INTERVIEWED = "INTERVIEWED", "Interviewed"
        OFFERED = "OFFERED", "Offered"
        HIRED = "HIRED", "Hired"
        REJECTED = "REJECTED", "Rejected"

    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey("jobs.JobPosting", on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    cover_letter = models.TextField(blank=True)
    ai_match_score = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ("candidate", "job")
        verbose_name = "Application"

    def __str__(self):
        return f"{self.candidate.email} → {self.job.title} ({self.status})"
