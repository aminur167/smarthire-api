"""Custom permissions for SmartHire."""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow only users with ADMIN role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsRecruiter(BasePermission):
    """Allow only users with RECRUITER role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "RECRUITER"


class IsCandidate(BasePermission):
    """Allow only users with CANDIDATE role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CANDIDATE"


class IsAdminOrRecruiter(BasePermission):
    """Allow ADMIN or RECRUITER roles."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("ADMIN", "RECRUITER")


class IsOwnerOrAdmin(BasePermission):
    """Allow object owner or admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        return obj == request.user or getattr(obj, "user", None) == request.user
