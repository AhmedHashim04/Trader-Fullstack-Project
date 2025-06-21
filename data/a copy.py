import json

# قائمة الصور بالترتيب
images = [
    "media/products/1.png", "media/products/2.png", "media/products/3.png", "media/products/4.webp", "media/products/5.png",
    "media/products/6.png", "media/products/7.webp", "media/products/8.png", "media/products/9.jpg", "media/products/10.jpeg",
    "media/products/11.png", "media/products/12.jpeg", "media/products/13.jpg", "media/products/14.jpeg", "media/products/15.jpeg",
    "media/products/16.jpeg", "media/products/17.webp", "media/products/18.jpg", "media/products/19.jpg", "media/products/20.jpg",
    "media/products/21.webp", "media/products/22.jpg", "media/products/23.jpg", "media/products/24.jpeg", "media/products/25.jpeg",
    "media/products/26.webp", "media/products/27.webp", "media/products/28.jpg", "media/products/29.webp", "media/products/30.jpg",
    "media/products/31.avif", "media/products/32.avif", "media/products/33.avif", "media/products/34.jpeg", "media/products/35.jpeg",
    "media/products/36.webp", "media/products/37.webp", "media/products/38.jpg", "media/products/39.jpg", "media/products/40.webp",
    "media/products/41.avif", "media/products/42.jpg", "media/products/43.jpg", "media/products/44.jpg", "media/products/45.jpg",
    "media/products/46.avif", "media/products/47.jpg", "media/products/48.webp", "media/products/49.jpg", "media/products/50.jpg",
    "media/products/51.jpeg", "media/products/52.jpg", "media/products/53.avif", "media/products/54.webp", "media/products/55.jpeg"
]

with open('data_converted.json', encoding='utf-8') as f:
    data = json.load(f)

img_idx = 0
for obj in data:
    if obj.get('model') == 'product.product':
        if img_idx < len(images):
            obj['fields']['image'] = images[img_idx]
            img_idx += 1
        else:
            obj['fields']['image'] = ""  # أو ضع None لو تحب

with open('data_converted_with_images.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("تم تحديث الصور بنجاح! الناتج: data_converted_with_images.json")