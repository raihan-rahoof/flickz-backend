from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_theatre_approval_email(theatre):
    subject = "Your Theatre Account has bee Approved !"
    current_site = 'flickz.onrender.com'
    email_body = render_to_string('theatre_approval.html',{
        'user':theatre.owner_name,
        'theatre' : theatre,
        'current_site': current_site,
    })

    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to = [theatre.user.email]
    )

    email.content_subtype = 'html'
    email.send()


def send_theatre_disapproval_email(theatre):
    subject = "Your Theatre Account Has Been Disapproved"
    current_site = "flickz.com"
    email_body = render_to_string(
        "theatre_disapproval_email.html",
        {
            "theatre": theatre,
            "current_site": current_site,
        },
    )

    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[theatre.user.email],
    )
    email.content_subtype = "html"
    email.send()
