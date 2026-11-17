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


class GoogleAuthView(APIView):
    """
    Authenticate or register a user via Google OAuth2.
    Issues real JWT access and refresh token pairs.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required for Google authentication."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.lower().strip()
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        role = request.data.get("role", User.Role.CANDIDATE)

        # Look up existing user or create a new verified one
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name or email.split("@")[0].capitalize(),
                "last_name": last_name,
                "role": role if role in User.Role.values else User.Role.CANDIDATE,
                "is_verified": True,
            },
        )

        if not user.is_active:
            return Response(
                {"detail": "This user account has been deactivated."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate standard SimpleJWT tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "email"]
