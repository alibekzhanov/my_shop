from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cart, Product, АvailabilityAlert
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        instance.cart.save()


@receiver(pre_save, sender=Product)
def availability_alert(sender, instance, **kwargs):
    
    queryset = sender.objects.filter(name = instance.name)

    if queryset.exists():
        prod = queryset[0]
        if prod.quantity == 0 and prod.quantity < instance.quantity:
            alerts = АvailabilityAlert.objects.filter(product = instance)
            for alert in alerts:
                send_mail(
                    f"Прибыла новая партия твоего заказа {alert.product.name[:6]}...",
                    f"На складе появился {alert.product.name} в количестве {alert.product.quantity} со скидочной цене {alert.product.discount_price}",
                    "olzhas2201@gmail.com",
                    [alert.user.email],
                    fail_silently=False,
                )
                alert.delete()
            