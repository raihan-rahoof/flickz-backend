from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .utils import send_generated_otp_to_email
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from datetime import date
from bookings.models import Bookings,OfflineBookings

from .models import OneTimePasswordTheatre, Theatre,Shows
from .serializers import (
    TheatreLoginSerializer,
    TheatreRegistrationSerializer,
    ShowMovieSerializer,
    ShowCreateSerializer,
    ShowListSerializer,
    ShowSerializer,
    ShowDetailSerialiser,
    UserSerializer,
    OfflineBookingSerializer,
    TheatreDashboardSerializer
)
from adminside.models import Movie


class TheatreRegisterView(generics.GenericAPIView):
    serializer_class = TheatreRegistrationSerializer

    def post(self,request):
        theatre_data = request.data
        serializer = self.serializer_class(data=theatre_data)
        if serializer.is_valid(raise_exception=True):
            theatre = serializer.save()
            user_email = theatre.user.email
            send_generated_otp_to_email(user_email)  
            return Response(
                {
                    "data": serializer.data,
                    "message": "A passcode has been sent to your mail to verify Email",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TheatreEmailVerification(generics.GenericAPIView):

    def post(self, request):
        try:
            passcode = request.data.get("otp")
            theatre_pass = OneTimePasswordTheatre.objects.get(code=passcode)
            theatre = theatre_pass.theatre
            user = theatre.user

            

            if not theatre.is_verified and not user.is_verified :
                theatre.is_verified = True
                user.is_verified = True
                user.save()
                theatre.save()

                return Response(
                    {"message": "Account verified successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid Otp,Try again"}, status=status.HTTP_204_NO_CONTENT
            )
        except OneTimePasswordTheatre.DoesNotExist:
            return Response(
                {"message": "Wrong Otp"}, status=status.HTTP_400_BAD_REQUEST
            )

class TheatreLoginView(generics.GenericAPIView):
    serializer_class = TheatreLoginSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# ---------------- Shows -----------------


class TheatreShowAddView(generics.ListCreateAPIView):
    queryset = Shows.objects.all()
    serializer_class = ShowCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter screens by the logged-in user's theatre
        return Shows.objects.filter(theatre=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShowCreateSerializer
        return ShowListSerializer


class TheatreMovieSelectView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = ShowMovieSerializer
    permission_classes = [IsAuthenticated]


class ShowDeleteView(generics.DestroyAPIView):
    queryset = Shows.objects.all()
    serializer_class = ShowSerializer

    def delete(self, request, *args, **kwargs):
        try:
            show = self.get_object()
            show.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------- user side available shows ----------------------
class AvailableShows(APIView):
    def get(self,request,movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'error':'Movie doesnt exists'},status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        shows = Shows.objects.filter(movie=movie,date__date__gte=today)
        serializer = ShowListSerializer(shows,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ShowDetailView(APIView):

    def get(self, request, show_id):
        try:
            show = Shows.objects.prefetch_related("bookings").get(id=show_id)
        except Shows.DoesNotExist:
            return Response(
                {"error": "Show not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # online bookings
        total_revenue_online = sum(booking.total_price for booking in show.bookings.all())
        tickets_sold_online = sum(len(booking.seats) for booking in show.bookings.all())

        # Offline bookings
        offline_bookings = OfflineBookings.objects.filter(show=show)
        total_revenue_offline = sum(booking.total_price for booking in offline_bookings)
        tickets_sold_offline = sum(len(booking.seats) for booking in offline_bookings)

        # Serialize offline bookings
        offline_bookings_serializer = OfflineBookingSerializer(offline_bookings, many=True)

        # Combined data
        total_revenue = total_revenue_online + total_revenue_offline
        tickets_sold = tickets_sold_online + tickets_sold_offline

        serializer = ShowDetailSerialiser(show)
        data = serializer.data
        data["total_revenue_online"] = total_revenue_online
        data["tickets_sold_online"] = tickets_sold_online
        data["total_revenue_offline"] = total_revenue_offline
        data["tickets_sold_offline"] = tickets_sold_offline
        data["total_revenue"] = total_revenue
        data["tickets_sold"] = tickets_sold
        data["offline_bookings"] = offline_bookings_serializer.data

        return Response(data, status=status.HTTP_200_OK)


class TheatreDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        # Calculate today's revenue
        todays_revenue = 0
        todays_shows = Shows.objects.filter(date=today)
        for show in todays_shows:
            todays_revenue += sum(
                booking.amount for booking in Bookings.objects.filter(show=show)
            )

        # Calculate monthly revenue
        monthly_revenue = 0
        monthly_shows = Shows.objects.filter(date__gte=start_of_month)
        for show in monthly_shows:
            monthly_revenue += sum(
                booking.amount for booking in Bookings.objects.filter(show=show)
            )

        # Calculate yearly revenue
        yearly_revenue = 0
        yearly_shows = Shows.objects.filter(date__gte=start_of_year)
        for show in yearly_shows:
            yearly_revenue += sum(
                booking.amount for booking in Bookings.objects.filter(show=show)
            )

        # Calculate expired shows
        expired_shows = Shows.objects.filter(date__lt=today).count()

        data = {
            "todays_revenue": todays_revenue,
            "monthly_revenue": monthly_revenue,
            "yearly_revenue": yearly_revenue,
            "expired_shows": expired_shows,
        }

        serializer = TheatreDashboardSerializer(data)
        return Response(serializer.data)
