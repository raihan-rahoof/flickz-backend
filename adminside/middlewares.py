from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from theatre_side.models import Theatre
from django.contrib.auth import get_user_model

User = get_user_model()


class CheckBlockedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                user = User.objects.get(id=request.user.id)
                if hasattr(user, "user_type") and user.user_type == "theatre":
                    try:
                        theatre = Theatre.objects.get(user=user)
                        if not theatre.is_active or not theatre.is_verified:
                            return JsonResponse(
                                {
                                    "detail": "Your account has been blocked or is not verified."
                                },
                                status=403,
                            )
                    except Theatre.DoesNotExist:
                        return JsonResponse(
                            {"detail": "Theatre profile not found."}, status=404
                        )
            except User.DoesNotExist:
                return JsonResponse({"detail": "User not found."}, status=404)
        return None
