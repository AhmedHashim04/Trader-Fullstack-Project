# Generated by Django 5.1.1 on 2025-05-18 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wishlist',
            field=models.ManyToManyField(blank=True, related_name='wishlist', to='product.product', verbose_name='Wishlist'),
        ),
    ]
