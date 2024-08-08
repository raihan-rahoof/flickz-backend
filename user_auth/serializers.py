from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_str, smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers,status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from .models import User, UserProfile
from .utils import send_normal_email


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Email address is already in use"
            )
        ]
    )
    phone = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Phone number is already in use"
            )
        ]
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "password2",
            "is_active",
        ]

    def validate(self, attrs):
        password = attrs.get("password", "")
        password2 = attrs.get("password2", "")

        if password != password2:
            raise serializers.ValidationError("The passwords do not match.")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            password=validated_data.get("password"),
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credentials. Please try again.")
        if user.user_type != 'normal':
            raise AuthenticationFailed('No Account with This Credentials')
        elif not user.is_active:
            raise AuthenticationFailed("Your Account has been Blocked due some Reason")
        user = authenticate(request, email=email, password=password, user_type="normal")

        if not user:
            raise AuthenticationFailed("invalid credentials try again")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        tokens = user.tokens()

        # Return the validated data with access and refresh tokens
        return {
            "email": user.email,
            "access_token": str(tokens.get("access")),
            "refresh_token": str(tokens.get("refresh")),
            "user_id": user.id,
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):

        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            frontend_site = "flickz.onrender.com" 
            relative_link = f"/reset-password-confirm/{uidb64}/{token}/"
            abslink = f"https://{frontend_site}{relative_link}"
            print(abslink)
            email_body = f"Hi {user.first_name} use the link below to reset your password {abslink}"
            data = {
                "email_body": email_body,
                "email_subject": "Reset your Password",
                "to_email": user.email,
            }
            send_normal_email(data)
        else:
            return Response({'error':'This Email Doesnt exists'},status=status.HTTP_404_NOT_FOUND)

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(
        max_length=100, min_length=6, write_only=True
    )
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        try:
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            password = attrs.get("password")
            confirm_password = attrs.get("confirm_password")

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")


class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_message = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs.get("refresh_token")

        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail("bad_token")


# ------------------  User Profile Serialisers -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone','email']
        read_only_fields = ["email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "birth_date",
            "gender",
            "address",
            "pincode",
            "city",
            "district",
            "state",
            "user_image",
            "is_mobile_verified",
        ]

    

class MobileVerificaitonSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["is_mobile_verified"]
