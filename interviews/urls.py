"""URL configuration for interviews app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.InterviewViewSet, basename="interview")

app_name = "interviews"

urlpatterns = [
    path("upcoming/", views.UpcomingInterviewsView.as_view(), name="upcoming"),
    path("", include(router.urls)),
]
