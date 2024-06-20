from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, validate_email

# Create your models here.
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .managers import UserManager

# Create your models here.

phone_regex = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must be 10 digits and contain only numbers.",
)

AUTH_PROVIDERS = {"email": "email", "google": "google"}


class User(AbstractBaseUser, PermissionsMixin):

    USER_TYPE_CHOICES = (
        ('normal','Normal User'),
        ('theatre','Theatre')
    )

    first_name = models.CharField(
        _("First Name"), max_length=100, blank=True, null=True
    )
    last_name = models.CharField(_("Last Name"), max_length=100, blank=True, null=True)
    email = models.EmailField(
        _("Email Address"), max_length=254, unique=True, validators=[validate_email]
    )
    phone = models.CharField(
        _("phone"),
        max_length=15,
        validators=[phone_regex],
        blank=True,
        null=True,
        unique=True,
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    auth_provider = models.CharField(
        max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get("email")
    )
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="normal"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self) -> str:
        return f"{self.user.first_name}-passcode"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    birth_date = models.DateField(_("birth_data"), null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=20, null=True, blank=True)
    address = models.TextField(_("address"), null=True, blank=True)
    pincode = models.CharField(_("pincode"), max_length=10, blank=True, null=True)
    city = models.CharField(_("city"), max_length=250, null=True, blank=True)
    district = models.CharField(_('district'),max_length=100,null=True,blank=True)
    state = models.CharField(_("state"), max_length=100, null=True, blank=True)
    user_image = models.ImageField(
        _("User Image"), upload_to="profile/", blank=True, null=True
    )

    def __str__(self) -> str:
        return f"{self.user.email} 's Profile"


# ------------------ Signals---------------------


@receiver(post_save, sender=User)
def create_or_update_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
