"""URL configuration for dashboard."""

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("stats/", views.DashboardStatsView.as_view(), name="stats"),
    path("jobs-overview/", views.JobsOverviewView.as_view(), name="jobs-overview"),
    path("requests/", views.RequestsSummaryView.as_view(), name="requests"),
    path("activity/", views.RecentActivityView.as_view(), name="activity"),
]
