from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """
    Send notification when a new order is created.
    """
    if created:
        # Send email to user
        subject = f"Your order {instance.id} has been placed"
        message = (
            f"Hi {instance.user.username},\n"
            f"Thank you for your purchase! Your order ID is {instance.id}.\n"
            f"We will notify you when the status changes.\n"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=True,
        )

        print(f"{subject}\n{message}\n{settings.DEFAULT_FROM_EMAIL,[instance.user.email],True,}")

        # Log the order creation
@receiver(post_save, sender=Order)
def order_status_updated(sender, instance, created, **kwargs):
    """
    Send notification when an order status is updated.
    """
    # if not created and 'status' in instance.get_dirty_fields():
    if not created :
        subject = f"Your order {instance.id} status updated"
        message = (
            f"Hi {instance.user.username},\n"
            f"Your order status is now: {instance.status}.\n"
        )
        # send_mail(
        #     subject,
        #     message,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [instance.user.email],
        #     fail_silently=True,
        # )
        print(f"{subject}\n{message}\n{settings.DEFAULT_FROM_EMAIL,[instance.user.email],True,}")