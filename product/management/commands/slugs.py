from django.core.management.base import BaseCommand
from django.utils.text import slugify
from product.models import Product, Category,Tag
from features.models import  Collection, Brand

class Command(BaseCommand):
    help = "Reset all product slugs to 'knowledge', adding unique suffixes if needed"

    def handle(self, *args, **kwargs):
        base_slug = "knowledge"
        used_slugs = set(Product.objects.values_list('slug', flat=True))
        counter = 0

        for product in Product.objects.all():
            if counter == 0:
                new_slug = base_slug
            else:
                new_slug = f"{base_slug}-{counter}"

            while new_slug in used_slugs:
                counter += 1
                new_slug = f"{base_slug}-{counter}"

            used_slugs.add(new_slug)
            product.slug = new_slug
            product.save(update_fields=["slug"])
            counter += 1

        self.stdout.write(self.style.SUCCESS("All product slugs updated successfully."))

        base_slug = "categorynono"
        used_slugs = set(Category.objects.values_list('slug', flat=True))
        counter = 0

        for product in Category.objects.all():
            if counter == 0:
                new_slug = base_slug
            else:
                new_slug = f"{base_slug}-{counter}"

            while new_slug in used_slugs:
                counter += 1
                new_slug = f"{base_slug}-{counter}"

            used_slugs.add(new_slug)
            product.slug = new_slug
            product.save(update_fields=["slug"])
            counter += 1

        self.stdout.write(self.style.SUCCESS("All Category slugs updated successfully."))

        base_slug = "Brara"
        used_slugs = set(Brand.objects.values_list('slug', flat=True))
        counter = 0

        for product in Brand.objects.all():
            if counter == 0:
                new_slug = base_slug
            else:
                new_slug = f"{base_slug}-{counter}"

            while new_slug in used_slugs:
                counter += 1
                new_slug = f"{base_slug}-{counter}"

            used_slugs.add(new_slug)
            product.slug = new_slug
            product.save(update_fields=["slug"])
            counter += 1

        self.stdout.write(self.style.SUCCESS("All Brand slugs updated successfully."))

        base_slug = "Trara"
        used_slugs = set(Tag.objects.values_list('slug', flat=True))
        counter = 0

        for product in Tag.objects.all():
            if counter == 0:
                new_slug = base_slug
            else:
                new_slug = f"{base_slug}-{counter}"

            while new_slug in used_slugs:
                counter += 1
                new_slug = f"{base_slug}-{counter}"

            used_slugs.add(new_slug)
            product.slug = new_slug
            product.save(update_fields=["slug"])
            counter += 1

        self.stdout.write(self.style.SUCCESS("All Tag slugs updated successfully."))

        base_slug = "Colo"
        used_slugs = set(Collection.objects.values_list('slug', flat=True))
        counter = 0

        for product in Collection.objects.all():
            if counter == 0:
                new_slug = base_slug
            else:
                new_slug = f"{base_slug}-{counter}"

            while new_slug in used_slugs:
                counter += 1
                new_slug = f"{base_slug}-{counter}"

            used_slugs.add(new_slug)
            product.slug = new_slug
            product.save(update_fields=["slug"])
            counter += 1

        self.stdout.write(self.style.SUCCESS("All Collection slugs updated successfully."))
