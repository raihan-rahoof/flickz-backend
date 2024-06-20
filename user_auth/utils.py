import random
from django.conf import settings
from django.core.mail import EmailMessage
from .models import User,OneTimePassword
from django.template.loader import render_to_string
from datetime import datetime


def send_generated_otp_to_email(email): 
    subject = "One time passcode for Email verification"
    otp=random.randint(100000, 999999)
    date = datetime.now().strftime("%Y-%m-%d")
    current_site="flickz.com"
    user = User.objects.get(email=email)
    email_body= render_to_string('emial_otp.html',{'user':user,'otp':otp,'current_site':current_site,'date':date})
    from_email=settings.EMAIL_HOST
    OneTimePassword.objects.create(user=user, code=otp)
    #send the email 
    d_email=EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
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