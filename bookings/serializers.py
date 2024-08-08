from rest_framework import serializers
from .models import Bookings,OfflineBookings
from theatre_side.serializers import ShowListSerializer

class BookingSerializer(serializers.ModelSerializer):
    show = ShowListSerializer()
    class Meta:
        model=Bookings
        fields = [
            "id",
            "show",
            "user",
            "seats",
            "seat_number",
            "total_price",
            "payment_status",
            "ticket_expiration",
            "booked_at",
            "stripe_payment_id",
        ]

class OfflineBookingSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = OfflineBookings
        fields = ['id','name','email','phone','seats','show','seat_number','total_price']
