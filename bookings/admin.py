from django.contrib import admin
from .models import Bookings,OfflineBookings
# Register your models here.
admin.site.register(Bookings)
admin.site.register(OfflineBookings)
