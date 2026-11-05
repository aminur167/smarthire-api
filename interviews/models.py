"""Models for the interviews app."""

from django.conf import settings
from django.db import models


class Interview(models.Model):
    """An interview session linked to an application."""

    class InterviewType(models.TextChoices):
        PHONE = "PHONE", "Phone Screen"
        VIDEO = "VIDEO", "Video Call"
        IN_PERSON = "IN_PERSON", "In-Person"
        TECHNICAL = "TECHNICAL", "Technical Round"
        HR = "HR", "HR Round"

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"
        NO_SHOW = "NO_SHOW", "No Show"

    application = models.ForeignKey(
        "candidates.Application", on_delete=models.CASCADE, related_name="interviews"
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conducted_interviews"
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    interview_type = models.CharField(max_length=20, choices=InterviewType.choices, default=InterviewType.VIDEO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=300, blank=True)
    notes = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]
        verbose_name = "Interview"

    def __str__(self):
        return f"{self.application} – {self.interview_type} on {self.scheduled_at:%Y-%m-%d %H:%M}"

    def save(self, *args, **kwargs):
        if self.rating is not None and not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        super().save(*args, **kwargs)
