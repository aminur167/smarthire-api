"""SmartHire URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
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
