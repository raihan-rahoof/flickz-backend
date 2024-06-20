import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ShowSeatReservation
from django.utils import timezone
from asgiref.sync import sync_to_async
from user_auth.models import User


class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "seats"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        seat_id = data["seat_id"]
        user_mail = data["user_mail"]
        action = data["action"]
        show_id = data["show_id"]

        user = await self.get_user_by_email(user_mail)
        user_id = user.id

        seat_reservation = await self.get_or_create_seat_reservation(show_id, seat_id)
        if action == "select":
            seat_reservation.selected_by_id = user_id
            seat_reservation.selected_at = timezone.now()
        elif action == "unselect":
            seat_reservation.selected_by_id = None
            seat_reservation.selected_at = None
        await self.save_seat_reservation(seat_reservation)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": f"seat_{action}",
                "seat_id": seat_id,
                "user_id": user_id,
                "show_id": show_id,
            },
        )

    async def seat_select(self, event):
        seat_id = event["seat_id"]
        user_id = event["user_id"]
        show_id = event["show_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "seat_selected",
                    "seat_id": seat_id,
                    "user_id": user_id,
                    "show_id": show_id,
                }
            )
        )

    async def seat_unselect(self, event):
        seat_id = event["seat_id"]
        user_id = event["user_id"]
        show_id = event["show_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "seat_unselected",
                    "seat_id": seat_id,
                    "user_id": user_id,
                    "show_id": show_id,
                }
            )
        )

    @sync_to_async
    def get_or_create_seat_reservation(self, show_id, seat_id):
        try:
            seat_reservation, created = ShowSeatReservation.objects.get_or_create(
                show_id=show_id, seat_id=seat_id
            )
            return seat_reservation
        except ShowSeatReservation.DoesNotExist:
            return None

    @sync_to_async
    def save_seat_reservation(self, seat_reservation):
        seat_reservation.save()

    @sync_to_async
    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
