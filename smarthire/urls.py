"""SmartHire URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def api_root_view(request):
    return JsonResponse({
        "status": "online",
        "service": "SmartHire API — AI-Powered Recruitment Management Platform",
        "version": "v1.0.0",
        "author": "Aminur Rahman",
        "endpoints": {
            "auth": "/api/v1/auth/token/",
            "accounts": "/api/v1/accounts/",
            "jobs": "/api/v1/jobs/postings/",
            "candidates": "/api/v1/candidates/applications/",
            "interviews": "/api/v1/interviews/",
            "dashboard": "/api/v1/dashboard/stats/",
            "admin": "/admin/",
        },
    })

urlpatterns = [
    path("", api_root_view, name="api_root"),
    path("admin/", admin.site.urls),
    # JWT Auth
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # App APIs
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/jobs/", include("jobs.urls")),
    path("api/v1/candidates/", include("candidates.urls")),
    path("api/v1/interviews/", include("interviews.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
