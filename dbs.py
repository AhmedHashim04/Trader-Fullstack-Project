
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
    activation_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Activation Key"))

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

class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    def get_total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    address = models.TextField(max_length=255, verbose_name=_("Address"), blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name=_("Country"), blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"), blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    paied = models.BooleanField(_("Paied"),default=False)
    confirmed = models.BooleanField(_("Confirmed"),default=False)
    confirmation_key = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = sum(item.get_total_price() for item in self.items.all())
        super().save(*args, **kwargs)

    def get_items(self):
        return self.items.all()

    def update_status(self, new_status):
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_total_price(self):
        return self.price * self.quantity

class Product(models.Model):
    name = models.CharField(max_length=40, verbose_name=_("Name"))
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name=_("Category"), blank=True, null=True)
    brand = models.ForeignKey('settings.Brand', on_delete=models.PROTECT, verbose_name=_("Brand"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Price"))
    cost = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Cost"))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created At"))
    # image = models.ImageField(upload_to='products/', verbose_name=_("Product Image"), blank=True, null=True)
    image = models.URLField(verbose_name=_("Image URL"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    viewed_by = models.ManyToManyField("account.Profile", verbose_name=_("Viewed By"), related_name="viewed_products", blank=True)
    tags = TaggableManager(verbose_name=_("Tags"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    overall_rating = models.FloatField(default=0.0, verbose_name=_("Overall Rating"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail', kwargs={'slug': self.slug})

    def is_in_stock(self):
        return self.stock > 0

    def update_overall_rating(self) -> None:
        reviews = self.product_review.all()
        if reviews.exists():
            try:
                average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                self.overall_rating = round(average_rating, 2) if average_rating is not None else 0
            except TypeError:
                self.overall_rating = 0
        else:
            self.overall_rating = 0
        self.save()

    @classmethod
    def calculate_overall_rating(cls, reviews: models.QuerySet['Review']) -> float:
        if not reviews.exists():
            return 0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / reviews.count()


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    parent = models.ForeignKey('self', limit_choices_to={'parent__isnull': True}, on_delete=models.CASCADE, verbose_name=_("Parent Category"), blank=True, null=True)
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    image = models.ImageField(upload_to='category_pictures/', verbose_name=_("Image"), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:category_detail', kwargs={'slug': self.slug})


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_review", verbose_name=_("Product"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_review", verbose_name=_("User"))
    content = models.TextField(max_length=1000, verbose_name=_("Review"),default="")
    rating = models.IntegerField(choices=RATING_CHOICES, default=3, verbose_name=_("Rating"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"

# Create your models here.
class Brand(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    name  = models.CharField(max_length=40)
    image = models.ImageField(upload_to='brand_pictures/', verbose_name=_("Image"), blank=True, null=True)
    desc  = models.TextField(_("Brand description"),max_length=1000,blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



    def get_absolute_url(self):
        return reverse('settings:brand_detail', kwargs={'slug': self.slug})

