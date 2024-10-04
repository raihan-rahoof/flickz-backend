from adminside.models import Movie
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from theatre_screen.models import Screen
from theatre_screen.serializers import ScreenSerializer
from user_auth.models import User
from adminside.serializers import ThatreListSerializer
from .models import Shows, Theatre
from bookings.models import Bookings,OfflineBookings
from django.utils.encoding import force_str, smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from user_auth.utils import send_normal_email

class TheatreRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Theatre
        fields = [
            "email",
            "password",
            "theatre_name",
            "owner_name",
            "license",
            "phone_number",
            "address",
            "city",
            "district",
            "state",
            "pincode",
            "google_maps_link",
        ]

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_theatre_user(email=email, password=password)
        theatre_profile = Theatre.objects.create(user=user, **validated_data)
        return theatre_profile


class TheatreLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")

        try:
            user = User.objects.get(email=email)
            theatre = Theatre.objects.get(user=user)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid Credentials , Please try again")

        if user.user_type != "theatre":
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active and not theatre.is_active:
            raise AuthenticationFailed(
                "Your account is Blocked by the Adminstration for some reason,Contact admin team for furthor informations"
            )

        if not user.is_verified and not theatre.is_verified:
            raise AuthenticationFailed("Your account is Out of verification,Contact admin team for furthur information")

        theatre_profile = authenticate(
            request, email=email, password=password, user_type="theatre"
        )
        if not theatre_profile:
            raise AuthenticationFailed("Invalid Credentials")
        if not theatre.admin_allow:
            raise AuthenticationFailed(
                "Your account is currently pending review by our administration team. We will update you on Mail with the status of your account approval within one business day. Thank you for your patience."
            )

        return {
            "email": user.email,
            "full_name": user.get_full_name,
            "id": user.id,
            "access_token": user.tokens().get("access"),
            "refresh_token": user.tokens().get("refresh"),
        }


class TheatrePasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):

        email = attrs.get("email")
        if not User.objects.filter(email=email,user_type='theatre').exists():
            raise ValidationError("This Email Doesn't Exist")
        user = User.objects.get(email=email)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        frontend_site = "flickz.onrender.com/theatre"
        relative_link = f"/reset-password-confirm/{uidb64}/{token}/"
        abslink = f"https://{frontend_site}{relative_link}"
        print(abslink)
        email_body = (
            f"Hi {user.email}, use the link below to reset your password {abslink}"
        )
        data = {
            "email_body": email_body,
            "email_subject": "Reset your Password",
            "to_email": user.email,
        }
        send_normal_email(data)

        return super().validate(attrs)


class TheatreSetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(
        max_length=100, min_length=6, write_only=True
    )
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        try:
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            password = attrs.get("password")
            confirm_password = attrs.get("confirm_password")

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")


class TheatreProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Theatre
        fields = [
            "owner_name",
            "theatre_name",
            "phone_number",
            "license",
            "address",
            "city",
            "district",
            "state",
            "pincode",
            "google_maps_link",
            
        ]

    def update(self, instance, validated_data):
        
        instance.owner_name = validated_data.get("owner_name", instance.owner_name)
        instance.theatre_name = validated_data.get(
            "theatre_name", instance.theatre_name
        )
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.license = validated_data.get("license", instance.license)
        instance.address = validated_data.get("address", instance.address)
        instance.city = validated_data.get("city", instance.city)
        instance.district = validated_data.get("district", instance.district)
        instance.state = validated_data.get("state", instance.state)
        instance.pincode = validated_data.get("pincode", instance.pincode)
        instance.google_maps_link = validated_data.get(
            "google_maps_link", instance.google_maps_link
        )

        instance.save()
        return instance


# ------------- Show Serialiser ---------------------------


class ShowMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class ShowCreateSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%I:%M %p", input_formats=["%I:%M %p"])
    end_time = serializers.TimeField(format="%I:%M %p", input_formats=["%I:%M %p"])
    class Meta:
        model = Shows
        fields = [
            "id",
            "show_name",
            "movie",
            "screen",
            "theatre",
            "date",
            "start_time",
            "end_time",
        ]


class ShowUpdateSerializer(serializers.ModelSerializer):
    date = serializers.DateField(input_formats=["%Y-%m-%d"])
    start_time = serializers.TimeField(input_formats=["%I:%M %p"])
    end_time = serializers.TimeField(input_formats=["%I:%M %p"])

    class Meta:
        model = Shows
        fields = [
            "show_name",
            "movie",
            "screen",
            "theatre",
            "date",
            "start_time",
            "end_time",
        ]

    def update(self, instance, validated_data):
        instance.show_name = validated_data.get("show_name", instance.show_name)
        instance.movie_id = validated_data.get("movie", instance.movie_id)
        instance.screen_id = validated_data.get("screen", instance.screen_id)
        instance.theatre_id = validated_data.get("theatre", instance.theatre_id)

        date = validated_data.get("date")
        if date:
            instance.date = date

        start_time = validated_data.get("start_time")
        if start_time:
            instance.start_time = start_time

        end_time = validated_data.get("end_time")
        if end_time:
            instance.end_time = end_time

        instance.save()
        return instance


class TheatreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theatre
        fields = [
            "theatre_name",
            "owner_name",
            "phone_number",
            "address",
            "city",
            "district",
            "state",
            "pincode",
            "google_maps_link",
        ]


class ShowListSerializer(serializers.ModelSerializer):
    movie = ShowMovieSerializer()
    screen = ScreenSerializer()
    theatre_details = serializers.SerializerMethodField()

    class Meta:
        model = Shows
        fields = [
            "id",
            "show_name",
            "movie",
            "screen",
            "theatre",
            "theatre_details",
            "date",
            "start_time",
            "end_time",
        ]

    def get_theatre_details(self, obj):
        try:
            theatre = Theatre.objects.get(user=obj.theatre)
            return TheatreSerializer(theatre).data
        except Theatre.DoesNotExist:
            return None

class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shows
        fields = '__all__'

# -------------- Show Managment Serialiser ------------------


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone"]


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Bookings
        fields = ["id", "user", "seats", "seat_number", "total_price", "payment_status"]

class ShowDetailSerialiser(serializers.ModelSerializer):
    bookings=BookingSerializer(many=True)
    movie = ShowMovieSerializer()
    screen = ScreenSerializer()
    theatre_details = serializers.SerializerMethodField()

    class Meta:
        model = Shows
        fields = [
            "id",
            "show_name",
            "movie",
            "screen",
            "theatre",
            "theatre_details",
            "date",
            "start_time",
            "end_time",
            "bookings",
        ]

    def get_theatre_details(self, obj):
        try:
            theatre = Theatre.objects.get(user=obj.theatre)
            return TheatreSerializer(theatre).data
        except Theatre.DoesNotExist:
            return None


class OfflineBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineBookings
        fields = [
            "id",
            "seats",
            "name",
            "email",
            "phone",
            "seat_number",
            "total_price",
            "payment_status",
            "show",
        ]


class TheatreDashboardSerializer(serializers.Serializer):
    todays_revenue = serializers.DecimalField(max_digits=10,decimal_places=2)
    monthly_revenue = serializers.DecimalField(max_digits=10,decimal_places=2)
    yearly_revenue = serializers.IntegerField()
    expired_shows = serializers.IntegerField()
