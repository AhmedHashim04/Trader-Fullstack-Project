import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

User = get_user_model()

class Profile(models.Model):
    """
    Advanced User Profile Model with best practices implementation
    """

    class Cities(models.TextChoices):
        CAIRO = 'القاهرة', _('القاهرة')
        GIZA = 'الجيزة', _('الجيزة')
        ISMAILIA = 'الاسماعيلية', _('الاسماعيلية')
        FAYOUM = 'الفيوم', _('الفيوم')
        MINYA = 'المنيا', _('المنيا')
        MENUFIA = 'المنوفية', _('المنوفية')
        NEW_VALLEY = 'الوادي الجديد', _('الوادي الجديد')
        QALYUBIA = 'القليوبية', _('القليوبية')
        SHARQIA = 'الشرقية', _('الشرقية')
        GHARBIA = 'الغربية', _('الغربية')
        DAQAHLIA = 'الدقهلية', _('الدقهلية')
        DAMIETTA = 'الدمياط', _('الدمياط')
        RED_SEA = 'البحرالاحمر', _('البحرالاحمر')

    class Countries(models.TextChoices):
        EGYPT = 'مصر', _('مصر')

    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile",verbose_name=_("User"))
    phone_number = models.CharField(_("Phone Number"),max_length=20,blank=True,null=True,validators=[RegexValidator(regex=r'^01[0125][0-9]{8}$',message=_("Enter a valid Egyptian phone number"))])
    city = models.CharField(_("City"),choices=Cities.choices,max_length=100,blank=True,null=True)
    country = models.CharField(_("Country"),choices=Countries.choices,max_length=100,blank=True,null=True,default=Countries.EGYPT)
    address = models.CharField(_("Address"),validators=[RegexValidator(regex=r'^[\u0600-\u06FF\s\d]+(?:\s[\u0600-\u06FF\s\d]+)*$',message=_("Enter a valid Egyptian Address in Arabic"))],max_length=255,blank=True,null=True)
    postal_code = models.CharField(_("Postal Code"),validators=[RegexValidator(regex=r'^(?:[1-9]\d{2}|[1-9]\d{4})$',message=_("Enter a valid Egyptian Postal Code"))],max_length=10,blank=True,null=True)
    profile_image = models.ImageField(_("Profile Image"),upload_to='profile_pictures/%Y/%m/%d/',blank=True,null=True,help_text=_("Upload a profile picture (max 2MB)"))
    date_of_birth = models.DateField(_("Date of Birth"),blank=True,null=True)
    wishlist = models.ManyToManyField('product.Product',verbose_name=_("Wishlist"),related_name="wishlist",blank=True)
    activation_key = models.CharField(_("Activation Key"),max_length=255,blank=True,null=True)
    activation_key_expires = models.DateTimeField(_("Activation Key Expires"),blank=True,null=True)
    date_joined = models.DateTimeField(_("Date Joined"),auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"),auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        # ordering = ['-date_joined']
        # indexes = [
        #     models.Index(fields=['city']),
        #     models.Index(fields=['date_joined']),
        # ]

    def save(self, *args, **kwargs):
        # Optimize and resize profile image before saving
        if self.profile_image:
            self.profile_image = self.optimize_image(self.profile_image)
            
        super().save(*args, **kwargs)

    def optimize_image(self, image):
        """Optimize profile image size and quality"""
        img = Image.open(image)
        
        # Convert to RGB if PNG
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Resize if too large
        if img.width > 800 or img.height > 800:
            img.thumbnail((800, 800))
            
        output = BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )

    @property
    def age(self):
        """Calculate user age based on date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def wishlist_count(self):
        """Count of items in wishlist with caching"""
        return self.wishlist.count()

    def is_activation_key_expired(self):
        """Check if activation key has expired"""
        if self.activation_key_expires:
            return timezone.now() > self.activation_key_expires
        return True

    # def get_city_display_ar(self):
    #     """Get Arabic city name directly"""
    #     return self.get_city_display()

