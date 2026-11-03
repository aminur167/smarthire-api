"""URL configuration for candidates app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.CandidateProfileViewSet, basename="candidateprofile")
router.register("applications", views.ApplicationViewSet, basename="application")

app_name = "candidates"

urlpatterns = [
    path("upload-resume/", views.ResumeUploadView.as_view(), name="upload-resume"),
    path("", include(router.urls)),
]
