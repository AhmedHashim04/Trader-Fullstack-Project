from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from product.models import Product


class Profile(models.Model):
    PRFuser          = models.OneToOneField(User, on_delete=models.CASCADE)
    PRFemail         = models.EmailField(max_length=100, verbose_name="Email")
    PRFdate_joined   = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="Date Joined")
    PRFslug          = models.SlugField(unique=True, blank=True, null=True, verbose_name="Profile Slug")
    PRFfirst_name    = models.CharField(max_length=50, verbose_name="First Name")
    PRFlast_name     = models.CharField(max_length=50, verbose_name="Last Name")
    PRFphone_number  = models.CharField(max_length=20, verbose_name="Phone Number", blank=True, null=True)
    PRFaddress       = models.TextField(max_length=255, verbose_name="Address", blank=True, null=True)
    PRFcity          = models.CharField(max_length=100, verbose_name="City", blank=True, null=True)
    PRFcountry       = models.CharField(max_length=100, verbose_name="Country", blank=True, null=True)
    PRFpostal_code   = models.CharField(max_length=10, verbose_name="Postal Code", blank=True, null=True)
    PRFprofile_image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name="Profile Image")
    PRFdate_of_birth = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    PRFcart          = models.ManyToManyField(Product, verbose_name=_("User cart It"),related_name='users_cart_it' , blank=True )
    PRFlove          = models.ManyToManyField(Product, verbose_name=_("User Love It"),related_name="users_love_it" , blank=True )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        
    def __str__(self):
        return f"{self.PRFuser.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.PRFslug:
            self.PRFslug = slugify(self.PRFuser.username)
        super(Profile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('profile', kwargs=self.PRFslug)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(PRFuser=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
