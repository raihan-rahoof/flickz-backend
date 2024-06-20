from adminside.models import Movie
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from theatre_screen.models import Screen
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()


class Theatre(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="theatre_profile",
    )
    theatre_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    license = models.ImageField(upload_to="license/", null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    google_maps_link = models.URLField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    admin_allow = models.BooleanField(default=False, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = _("Theatre Profile")
        verbose_name_plural = _("Theatre Profiles")

    def __str__(self):
        return self.theatre_name


class OneTimePasswordTheatre(models.Model):
    theatre = models.OneToOneField(Theatre, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self) -> str:
        return f"{self.theatre.theatre_name}-passcode"


class Shows(models.Model):
    show_name = models.CharField(max_length=100, blank=True, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey('theatre_screen.Screen',on_delete=models.CASCADE,null=True)
    theatre = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.movie.title} - {self.screen} - {self.date} {self.start_time}"
