from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from product.models import Product
from django.core.validators import RegexValidator

import uuid

class Profile(models.Model):

    id             = models.UUIDField(_("ID"), primary_key=True, editable=False , default=uuid.uuid4)
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile" ,verbose_name=_("User"))
    email          = models.EmailField(max_length=100, verbose_name=_("Email"))
    phone_number   = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address        = models.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\u0600-\u06FF\s\d]+(?:\s[\u0600-\u06FF\s\d]+)*$',
                message="Enter a valid Egyptian Address in Arabic"
            )
        ],
        max_length=255,
        verbose_name=_("Address"),
        blank=True,
        null=True
    )
    CITY_CHOICES = [
        ('الجيزة', 'الجيزة'),
        ('القاهرة', 'القاهرة'),
        ('الاسماعيلية', 'الاسماعيلية'),
        ('الفيوم', 'الفيوم'),
        ('المنيا', 'المنيا'),
        ('المنوفية', 'المنوفية'),
        ('الوادي الجديد', 'الوادي الجديد'),
        ('القليوبية', 'القليوبية'),
        ('الشرقية', 'الشرقية'),
        ('الغربية', 'الغربية'),
        ('الدقهلية', 'الدقهلية'),
        ('الدمياط', 'الدمياط'),
        ('البحرالاحمر', 'البحرالاحمر'),
    ]
    city           = models.CharField(
        choices=CITY_CHOICES,
        max_length=100,
        verbose_name=_("City"),
        blank=True,
        null=True
    )
    country        = models.CharField(
        choices=[('مصر', 'مصر')],
        max_length=100,
        verbose_name=_("Country"),
        blank=True,
        null=True
    )
    postal_code    = models.CharField(
        validators=[
            RegexValidator(
                regex=r'^(?:[1-9]\d{2}|[1-9]\d{4})$',
                message="Enter a valid Egyptian Postal Code"
            )
        ],
        max_length=10,
        verbose_name=_("Postal Code"),
        blank=True,
        null=True
    )
    profile_image  = models.ImageField(upload_to='profile_pictures/', verbose_name=_("Profile Image"), blank=True, null=True)
    date_of_birth  = models.DateField(blank=True, null=True, verbose_name=_("Date of Birth"))
    wishlist       = models.ManyToManyField(Product, verbose_name=_("Wishlist"), related_name="wishlist", blank=True)
    activation_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Activation Key"))
    date_joined    = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined"))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    @property
    def wishlist_count(self):
        return self.wishlist.count()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        
        instance.profile.save()
