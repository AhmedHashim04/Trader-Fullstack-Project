import json

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

# بناء جداول تحويل الاسم إلى id
brand_map = {}
category_map = {}
tag_map = {}

for obj in data:
    if obj.get('model') == 'features.brand':
        brand_map[obj['fields']['name']] = obj['pk']
    if obj.get('model') == 'product.category':
        category_map[obj['fields']['name']] = obj['pk']
    if obj.get('model') == 'product.tag':
        tag_map[obj['fields']['name']] = obj['pk']

for obj in data:
    if obj.get('model') == 'product.product':
        fields = obj['fields']
        # category
        if isinstance(fields.get('category'), str):
            cat_name = fields['category']
            fields['category'] = category_map.get(cat_name, None)
        # brand
        if isinstance(fields.get('brand'), str):
            brand_name = fields['brand']
            fields['brand'] = brand_map.get(brand_name, None)
        # tags
        if isinstance(fields.get('tags'), list):
            fields['tags'] = [tag_map.get(tag, None) for tag in fields['tags'] if tag in tag_map]

with open('data_converted.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Done! Output: data_converted.json")