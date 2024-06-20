from django.db import models
from theatre_side.models import Shows
from user_auth.models import User

# Create your models here.
class Bookings(models.Model):
    show = models.ForeignKey(Shows,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    seats = models.JSONField(default=list)
    seat_number = models.JSONField(default=list)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"booking by {self.user} for {self.show.movie.title} on {self.show.date}"
