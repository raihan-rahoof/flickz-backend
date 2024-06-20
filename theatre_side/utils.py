import random
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import datetime
from .models import Theatre,OneTimePasswordTheatre
from django.utils.translation import gettext_lazy as _
from user_auth.models import User

def send_generated_otp_to_email(email): 
    subject = "One time passcode for Email verification"
    otp=random.randint(1000, 9999)
    date = datetime.now().strftime("%Y-%m-%d")
    current_site="flickz.com"
    try:
        user = User.objects.get(email=email)
        theatre = Theatre.objects.get(user=user)
    except User.DoesNotExist:
        raise ValueError(_("User with this email does not exist"))
    except Theatre.DoesNotExist:
        raise ValueError(_("Theatre profile associated with this user does not exist"))

    email_body= render_to_string('email_otp.html',{'user':theatre,'otp':otp,'current_site':current_site,'date':date})
    from_email=settings.EMAIL_HOST
    OneTimePasswordTheatre.objects.create(theatre=theatre, code=otp)
    # send the email
    d_email=EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[theatre.user.email])
    d_email.content_subtype = "html"
    d_email.send()

def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
