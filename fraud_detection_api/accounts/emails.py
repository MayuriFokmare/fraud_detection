from django.core.mail import send_mail
from django.conf import settings

def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}\n\nValid for 30 minutes."
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])