
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/',include('user_auth.urls')),
    path('api/v1/auth/',include('social_accounts.urls')),
    path('api/v1/cadmin/',include('adminside.urls')),
    path('api/v1/theatre/',include('theatre_side.urls')),
    path('api/v1/home/',include('users.urls')),
    path('api/v1/screen/',include('theatre_screen.urls')),
    path('api/v1/booking/',include('bookings.urls'))


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)