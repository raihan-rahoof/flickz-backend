import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from theatre_screen.models import Seat,Section , ShowSeatReservation
from theatre_side.models import Shows 
from .serializers import BookingSerializer,OfflineBookingSerializer
from rest_framework import generics
from user_auth.models import User
from .models import Bookings , OfflineBookings
from django.utils import timezone


# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        show_id = request.data.get("show_id")
        seats = request.data.get("seats")
        seat_numbers = request.data.get("seat_numbers")
        show = Shows.objects.get(id=show_id)
        user = request.user

        total_price = 0
        for seat_id in seats:
            try:
                seat = Seat.objects.get(id=seat_id)
                section = seat.section
                total_price += section.price
            except Seat.DoesNotExist:
                return Response(
                    {"error": f"Seat with id {seat_id} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        poster_url = request.build_absolute_uri(show.movie.poster.url)
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": show.movie.title,
                                "images": [
                                    request.build_absolute_uri(show.movie.poster.url)
                                ],
                            },
                            "unit_amount": int(total_price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{settings.FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment-failed",
            )

            booking = Bookings.objects.create(
                show=show,
                user=user,
                seats=seats,
                seat_number = seat_numbers,
                total_price=total_price,
                stripe_payment_id=checkout_session.id,
                payment_status="Pending",
            )

            return Response({"id": checkout_session.id}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stripe_payment_id = request.query_params.get("session_id")
        bookings = Bookings.objects.get(stripe_payment_id=stripe_payment_id)
        print('!!!!!!!!!!!!!!!a;klsdjksaf 0000000001111111111111111')
        bookings.payment_status = "Paid"
        bookings.save()

        

        for seat_id in bookings.seats:
            try:
                seat = ShowSeatReservation.objects.get(seat=seat_id)
                seat.is_reserved = True
                seat.reserved_by = bookings.user
                seat.save()
            except Seat.DoesNotExist:
                continue
        serializer = BookingSerializer(bookings)

        return Response({"status": "Payment_successful" , "details":serializer.data}, status=status.HTTP_200_OK)


class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"status": "Payment Canceled"}, status=status.HTTP_200_OK)


class HandleOfflineBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OfflineBookingSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            show_id = request.data.get("show")
            seats = request.data.get("seats")
            seat_nums = request.data.get("seat_nums")
            name = request.data.get("name")
            phone = request.data.get("phone")
            email = request.data.get("email")
            total_price = request.data.get("total_price")

            try:
                show = Shows.objects.get(id=show_id)
            except Shows.DoesNotExist:
                return Response(
                    {"error": f"Show with id={show_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            booking = OfflineBookings.objects.create(
                show=show,
                seats=seats,
                name=name,
                email=email,
                phone=phone,
                seat_number=seat_nums,
                total_price=total_price,
                payment_status="Paid",
            )

            booking.save()

            # Mark seats as reserved
            for seat_id in booking.seats:
                try:
                    seat = Seat.objects.get(id=seat_id)
                    reservation, created = ShowSeatReservation.objects.get_or_create(
                        show=show,
                        seat=seat,
                        is_reserved=True
                    )
                    if not created:
                        reservation.is_reserved = True
                        reservation.save()
                except ShowSeatReservation.DoesNotExist:
                    return Response(
                        {"error": "no seat found with this id"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- Booking details ------------------------------------

class TicketsListView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        try:
            tickets=Bookings.objects.filter(user=request.user.id).order_by('-booked_at')

            for ticket in tickets:
                expiration_time = ticket.show.end_time

                if timezone.now() > expiration_time:
                    tickets.ticket_expiration = True
                

            serializer = BookingSerializer(tickets,many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error':'user or booking not available'},status=status.HTTP_404_NOT_FOUND)
