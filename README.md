# 🛒 Trader - E-commerce Platform

![Trader](https://github.com/user-attachments/assets/c0f72baf-8294-47a1-81f1-6021407dbe03)

**Trader** is a full-featured modern e-commerce platform built with **Django** and **PostgreSQL**.  
Inspired by **Noon**, it provides product and order management, integrated payment systems (e.g. **Vodafone Cash**), advanced filtering, CSV tools, and a responsive UI using **Bootstrap**.

---

## 🚀 Features

- 🧾 Product & Category Management with inventory control  
- 💳 Secure Payments, including Vodafone Cash integration  
- 🛍️ Shopping Cart & Order Management  
- 📊 CSV Import/Export for product data  
- ⏱️ Background Tasks using Redis (e.g., order notifications)  
- 🎨 Responsive Frontend (Bootstrap + HTML5 + CSS3)  
- 🧪 Pytest-based Test Coverage  
- 💌 Email Notifications (orders, password resets, promotions)  
- 📄 PDF Invoice Generation  
- 💬 Product Reviews & Ratings  
- 💚 Wishlist System  
- 👤 User Profiles with multi-address support  
- 🔍 Advanced Filtering (price, rating, brand...)  
- 📦 Order Tracking (Processing → Shipped → Delivered)  
- 🛒 Related Products & "Bought Together" Suggestions  
- 📃 Static Pages (About, Terms, Privacy...)  
- 🚚 Region-Based Shipping Calculations  
- ⚡ Redis Caching for Products/Categories  
- 🔐 Admin Activity Logging  

---

## 🧪 Upcoming Features

- 📢 Advertisements System for Products  
- 🧵 Product Variants (Size, Color, etc.)  
- ⚖️ Shipping Weight Calculations  
- 📊 Admin Tools (Sales Dashboard, Bulk Edits, Discount Codes)  
- 🌐 Multi-Language & Multi-Currency Support  
- 🔐 JWT / OAuth2 Authentication, Rate Limiting, API Security  

---

## 🛠️ Tech Stack

| Layer         | Tech                          |
|---------------|-------------------------------|
| Backend       | Django (Python)               |
| Database      | PostgreSQL                    |
| Frontend      | HTML, CSS, JS, Bootstrap      |
| Async Tasks   | Celery + Redis                |
| Testing       | Pytest                        |

---

## ⚙️ Getting Started

### 🔹 1. Install Python

**Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows**: Download from [python.org](https://www.python.org/downloads/)

---

### 🔹 2. Install PostgreSQL

**Linux**:
```bash
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

**Windows**: [Install PostgreSQL](https://www.postgresql.org/download/)

Create database and user:
```sql
CREATE DATABASE trader_db;
CREATE USER trader_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE trader_db TO trader_user;
```

---

### 🔹 3. Clone & Setup Project

```bash
git clone https://github.com/AhmedHashim04/Trader-Fullstack-Project.git
cd Trader-Fullstack-Project
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 🔹 4. Apply Migrations

```bash
python manage.py migrate
python manage.py runserver
```

---

### 🔹 5. Redis & Celery (Linux)

```bash
sudo apt install redis
sudo service redis start
celery -A trader worker -l info
```

---

## 🧪 Run Tests

```bash
pytest
```

---

## 📁 Project Structure

<<<<<<< HEAD
<details>
<summary>Click to view simplified structure</summary>
=======
> _UI screenshots and GIFs below to showcase the frontend._
![image](https://github.com/user-attachments/assets/660522d4-138d-42f1-a1c3-8eaf49e9cd31)

- ![Homepage](screenshots/homepage.png)
- ![Product Detail](screenshots/product-detail.png)
- ![Cart](screenshots/cart.png)
- ![Checkout](screenshots/checkout.png)
- ![Admin Panel](screenshots/admin.png)

---

## 📁 Project Structure (simplified)
>>>>>>> a4a338fc396ea5dab7f786828a5492b82e42ef94

```bash
├── account/
├── cart/
├── contact/
├── coupon/
├── features/
├── home/
├── logs/
├── manage.py
├── media/
├── order/
├── payment/
├── product/
├── project/     # settings & URLs
├── static/
├── templates/
├── README.md
└── requirements.txt
```

</details>

---

## 🖼️ Screenshots

![image](https://github.com/user-attachments/assets/660522d4-138d-42f1-a1c3-8eaf49e9cd31)
![image](https://github.com/user-attachments/assets/d092eaaa-138c-4e78-8dc1-3dbb51855c70)
![image](https://github.com/user-attachments/assets/a84cbfd4-7dd8-494d-8ff5-56be4f473028)
![image](https://github.com/user-attachments/assets/ffe2d15e-7f9e-4944-9801-823294e83fd8)
![image](https://github.com/user-attachments/assets/0b94e1ff-75b0-45aa-b968-8c588a1d70fd)
![image](https://github.com/user-attachments/assets/37afcc6d-dfd6-4e15-8501-0075e7dd21b9)
![image](https://github.com/user-attachments/assets/fdf059b0-16f6-43cd-b7a6-057d35bbc5fa)
![image](https://github.com/user-attachments/assets/5e6511c9-ff1c-42d2-9db7-74f65fb5bd6e)
![image](https://github.com/user-attachments/assets/c9d42df1-3478-4086-887e-27eebdedba85)
![image](https://github.com/user-attachments/assets/6c2d03e9-07fb-42ef-bca6-da70b9902bf7)
![image](https://github.com/user-attachments/assets/e8c2f654-37e4-4866-9e06-1b3a0436ed91)
![image](https://github.com/user-attachments/assets/4e4a7fe0-60f2-4eef-9d70-2a21948f7c08)
![image](https://github.com/user-attachments/assets/442baf64-9202-4962-875a-29fc76bbcf36)
![image](https://github.com/user-attachments/assets/495339d3-1d19-4889-ab7d-51166866d0d3)
![image](https://github.com/user-attachments/assets/857a9176-51b7-4a93-b1a2-d7a966b782f6)
![image](https://github.com/user-attachments/assets/7d1113e1-b2b9-4c45-85a5-1fb122de43c7)
![image](https://github.com/user-attachments/assets/fd560cd3-7fca-4289-a45a-4d0056f97a63)
![image](https://github.com/user-attachments/assets/8d85c08a-c0ba-431e-b659-91de3ac02274)
![image](https://github.com/user-attachments/assets/810c745e-5e63-40b4-b4be-da57a91ace21)
![image](https://github.com/user-attachments/assets/aeccbe02-97ab-4204-bbe4-193393f902e9)
![image](https://github.com/user-attachments/assets/fb583d17-bbcf-4b82-977a-a45c8100ebdc)
![image](https://github.com/user-attachments/assets/8f405c5b-8284-4e16-94e9-45cdf982307c)
![image](https://github.com/user-attachments/assets/4e8e6032-d8fc-4549-ba93-5d4d67224d12)
![image](https://github.com/user-attachments/assets/8f8c81e9-0948-42db-acbb-1e78b6963efe)
![image](https://github.com/user-attachments/assets/c65fdc82-1a13-4155-b6d4-8f9d3829273a)
![image](https://github.com/user-attachments/assets/20599c8b-f8ba-4b73-8ea3-88ae51d66cf9)
![image](https://github.com/user-attachments/assets/ef264d75-1961-4ed2-880b-b3e2a3b447b1)
![image](https://github.com/user-attachments/assets/fb2e1b50-e15f-43b1-a5ec-34ca00093e86)
![image](https://github.com/user-attachments/assets/4a01a42c-5b2a-44e1-8303-84a32c736c2a)
![image](https://github.com/user-attachments/assets/7c6be4e5-31e1-4904-b1ac-0a8c814d5522)
![image](https://github.com/user-attachments/assets/957c69d6-14ba-4430-9775-389b2f34dcd0)
---

## 👤 Author

**Ahmed Hashim**  
[GitHub Profile](https://github.com/AhmedHashim04)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ⭐ Support & Contribution

If you like this project, please ⭐ the repo and feel free to fork or contribute via PR.  
Suggestions, bug reports, and feature requests are always welcome!