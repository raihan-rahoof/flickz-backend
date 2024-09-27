from rest_framework.response import Response
from django.utils.deprecation import MiddlewareMixin
from theatre_side.models import Theatre
from rest_framework import status

class CheckBlockedMiddleware(MiddlewareMixin):
    def process_request(self,request):
        user = request.user
        if user.is_authenticated:
            if user.user_type == 'theatre':
                try:
                    theatre = Theatre.objects.get(user=user)
                    if not theatre.is_active or not theatre.admin_allow:
                        return Response(
                                {"detail": "Your account has been blocked or is pending admin approval."},
                                status=status.HTTP_403_FORBIDDEN
                            )
                except Theatre.DoesNotExist:
                        
                        return Response(
                            {"detail": "Theatre profile not found."},
                            status=status.HTTP_404_NOT_FOUND
                        )