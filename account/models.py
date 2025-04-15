from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from product.models import Product
import uuid

class Profile(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, editable=False , default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(max_length=100, verbose_name=_("Email"))
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_("Date Joined"))
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address = models.TextField(max_length=255, verbose_name=_("Address"), blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name=_("Country"), blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"), blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name=_("Profile Image"))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("Date of Birth"))
    wishlist = models.ManyToManyField(Product, verbose_name=_("Favorite Products"), related_name="loved_by_users", blank=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def wishlist_count(self):
        return self.wishlist.count()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
