from rest_framework import serializers
from .models import Bookings
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
            "stripe_payment_id",
        ]
