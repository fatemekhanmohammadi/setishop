from celery import shared_task
from django.core.mail import send_mail

# =============================================================================


@shared_task
def send_password_reset_email(email, reset_link):
    send_mail(
        subject="بازیابی رمز عبور",
        message=f"برای تغییر رمز عبور، روی این لینک کلیک کنید:\n{reset_link}",
        from_email="noreply@setishop.com",
        recipient_list=[email],
    )


# =============================================================================
