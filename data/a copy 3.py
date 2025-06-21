import os
import django
import sys

# أضف مسار المشروع إلى PYTHONPATH
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

# تهيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from product.models import Product
import json

def export_products_to_json():
    products = Product.objects.all().values_list('id', 'name')
    product_data = [{"id": str(id), "name": name} for id, name in products]
    
    with open('products_ids.json', 'w') as f:
        json.dump(product_data, f, indent=2)
    
    print("تم تصدير البيانات إلى ملف products_ids.json")

if __name__ == "__main__":
    export_products_to_json()