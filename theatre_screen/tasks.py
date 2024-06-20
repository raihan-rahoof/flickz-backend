from celery import shared_task
from django.utils import timezone
from .models import Seat


@shared_task
def release_unbooked_seats():
    now = timezone.now()
    unbooked_seats = Seat.objects.filter(
        is_reserved=False, selected_at__lt=now - timezone.timedelta(minutes=5)
    )

    for seat in unbooked_seats:
        seat.selected_by=None
        seat.selected_at=None
        seat.save()