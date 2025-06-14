# Generated by Django 5.2.1 on 2025-06-14 23:59

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('features', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=40, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(max_length=1000, verbose_name='Description')),
                ('image', models.ImageField(blank=True, null=True, upload_to='category_pictures/', verbose_name='Image')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('parent', models.ForeignKey(blank=True, limit_choices_to={'parent__isnull': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.category', verbose_name='Parent Category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=40, verbose_name='Name')),
                ('description', models.TextField(max_length=1000, verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Cost')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Product Image')),
                ('slug', models.SlugField(blank=True, max_length=255, null=True, unique=True)),
                ('stock', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Stock')),
                ('overall_rating', models.FloatField(default=0.0, editable=False, verbose_name='Overall Rating')),
                ('is_available', models.BooleanField(db_index=True, default=True, verbose_name='Is Available')),
                ('discount', models.DecimalField(decimal_places=2, default=0, help_text='Discount percentage (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Discount')),
                ('trending', models.BooleanField(db_index=True, default=False, help_text='Is this product trending?', verbose_name='Trending')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='features.brand', verbose_name='Brand')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='product.category', verbose_name='Category')),
                ('viewed_by', models.ManyToManyField(blank=True, related_name='viewed_products', to='account.profile', verbose_name='Viewed By')),
                ('tags', models.ManyToManyField(blank=True, related_name='products', to='product.tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='', max_length=1000, verbose_name='Review')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=3, verbose_name='Rating')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='product.product', verbose_name='Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
                'ordering': ['-created_at'],
                'constraints': [models.UniqueConstraint(fields=('product', 'user'), name='unique_product_review')],
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['-overall_rating'], name='rating_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'brand'], name='category_brand_idx'),
        ),
    ]
