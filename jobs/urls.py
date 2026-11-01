"""URL configuration for jobs app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("postings", views.JobPostingViewSet, basename="jobposting")
router.register("departments", views.DepartmentViewSet, basename="department")

app_name = "jobs"

urlpatterns = [
    path("", include(router.urls)),
]
