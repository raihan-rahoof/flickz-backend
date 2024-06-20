from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email"))

    def create_user(self, email, password=None, first_name=None, last_name=None,phone=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Base User: An email address is required"))

        if extra_fields.get('user_type') != 'theatre':
            if not first_name:
                raise ValueError(_("Users must submit a first name"))
            if not last_name:
                raise ValueError(_("Users must submit a last name"))
            if not phone:
                raise ValueError(_("Users must submit a phone number"))
        else:
            first_name = first_name or ''
            last_name = last_name or ''
            phone = phone or None

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone= phone,
            **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user.save(using=self._db)

        return user

    def create_superuser(
        self, first_name, last_name, email, phone, password, **extra_fields
    ):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superusers must have is_superuser=True"))

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superusers must have is_staff=True"))

        if not password:
            raise ValueError(_("Superusers must have a password"))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Admin User: and email address is required"))

        user = self.create_user(
            first_name, last_name, email, phone, password, **extra_fields
        )

        user.save()

        return user

    def create_theatre_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("user_type", "theatre")
        user = self.create_user(email=email, password=password, **extra_fields)

        return user
