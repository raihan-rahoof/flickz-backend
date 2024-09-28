import json

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    force_str,
    smart_bytes,
    smart_str,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import OneTimePassword, User, UserProfile
from .serializers import (
    LoginSerializer,
    LogoutUserSerializer,
    MobileVerificaitonSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)
from .utils import send_generated_otp_to_email

# Create your views here.


class UserRegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_generated_otp_to_email(user["email"])
            print(user)
            return Response(
                {
                    "data": user,
                    "message": f"hi {user_data.get('first_name','')} thanks for signing up a passcode has be sent to verify your email",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get("otp")
            user_pass = OneTimePassword.objects.get(code=passcode)
            user = user_pass.user

            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response(
                    {"message": "account verified succssfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid OTP,Try again"}, status=status.HTTP_204_NO_CONTENT
            )
        except OneTimePassword.DoesNotExist:
            return Response(
                {
                    "message": "passcode not provided",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequest(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "we have sent you a email to reset password"},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"message": "token is invalid or has expired"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {
                    "success": True,
                    "message": "credentials is valid",
                    "uidb64": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )

        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {"message": "token is invalid or has expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "password reset is succesful"},
            status=status.HTTP_200_OK,
        )


class LogoutApiView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_active:
            data = {"msg": "User is inactive"}
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        data = {"msg": "It works"}
        return Response(data, status=status.HTTP_200_OK)


# ------------------ User Profile ----------------------------


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user.id
            details = User.objects.select_related("profile").get(id=user)
            serializer = UserProfileSerializer(details.profile)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            details = User.objects.select_related("profile").get(id=user_id)

            # Update User fields
            user_data = json.loads(request.data.get("user", "{}"))
            details.first_name = user_data.get("first_name", details.first_name)
            details.last_name = user_data.get("last_name", details.last_name)
            details.phone = user_data.get("phone", details.phone)
            details.save()

            # Update UserProfile fields
            profile = details.profile
            profile.birth_date = request.data.get("birth_date", profile.birth_date)
            profile.gender = request.data.get("gender", profile.gender)
            profile.address = request.data.get("address", profile.address)
            profile.pincode = request.data.get("pincode", profile.pincode)
            profile.city = request.data.get("city", profile.city)
            profile.district = request.data.get("district", profile.district)
            profile.state = request.data.get("state", profile.state)
            if "user_image" in request.data:
                profile.user_image = request.data["user_image"]
            profile.save()

            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ProfileMobileVerificationHandle(APIView):
    def patch(self, request):
        serializer = MobileVerificaitonSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=request.user.id)
                profile = UserProfile.objects.get(user=user)

                profile.is_mobile_verified = True
                profile.save()
                profile_serializer = MobileVerificaitonSerializer(profile)

                return Response(
                    {
                        "message": "Mobile number verified successfully",
                        "user_profile": profile_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "user not found"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
