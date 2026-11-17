"""Views for accounts app."""

from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
)
from .permissions import IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user and return JWT tokens."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change the authenticated user's password."""

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password updated successfully."})


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["role", "is_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "email"]
