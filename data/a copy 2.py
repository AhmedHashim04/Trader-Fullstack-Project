import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from product.models import Product
from features.models import ProductImage
# مسار مجلد الفولدرات
BASE_DIR = "/home/ahmed/Downloads"

# جلب أول 56 منتج بترتيب الـ id
products = Product.objects.all().order_by("id")[:56]

for index, product in enumerate(products, start=1):
    folder_path = os.path.join(BASE_DIR, str(index))
    if not os.path.exists(folder_path):
        print(f"❌ فولدر {folder_path} غير موجود")
        continue

    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            product_image = ProductImage(product=product)
            product_image.image.save(image_file, django_file, save=True)
            print(f"✅ أُضيفت الصورة {image_file} للمنتج {product.name}")