from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginUserView,
    LogoutApiView,
    PasswordResetConfirm,
    PasswordResetRequest,
    SetNewPasswordView,
    TestingAuthenticatedReq,
    UserProfileView,
    UserRegisterView,
    VerifyUserEmail,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("verify-email/", VerifyUserEmail.as_view(), name="verify"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("testauth/", TestingAuthenticatedReq.as_view(), name="testauth"),
    path("password-reset/", PasswordResetRequest.as_view(), name="password-reset"),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        PasswordResetConfirm.as_view(),
        name="reset-password-confirm",
    ),
    path("set-new-password/", SetNewPasswordView.as_view(), name="set-new-password"),
    path("logout/", LogoutApiView.as_view(), name="logout"),
    path("user-profile/", UserProfileView.as_view(), name="userprofile"),
]
