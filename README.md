
# 🛒 Trader - E-commerce Platform

**Trader** is a fully-featured e-commerce platform built with Django and PostgreSQL. Inspired by Noon, it includes product management, a full order system, integrated payment methods (including Vodafone Cash), CSV import/export, and a modern frontend using Bootstrap.

---

## 🚀 Features

- 🧾 Product and category management with inventory control
- 💳 Secure payment system (including Vodafone Cash integration)
- 🛍️ Shopping cart and order management
- 📊 Upload/download products using CSV files
- ⏱️ Background tasks with Redis & Celery (e.g., order notifications)
- 🎨 Responsive frontend using Bootstrap, HTML5, and CSS3
- 🧪 Full test coverage using Pytest
- 💌 Email Notifications (for orders, password reset, promotions)
- 🧾 Invoices & Order History (PDF export, detailed receipts)
- 💬 Product Reviews and Ratings
- 💚 Wishlist / Favorites
- 👥 User Profiles & Address Book (multiple addresses for shipping)
- 🔎 Advanced Search & Filtering (by price, rating, brand, etc.)
- 📦 Order Tracking System (Even basic status: Processing → Shipped → Delivered)

## 🚧 New Features in Development

### 👥 User Experience Enhancements
- User profiles with support for multiple shipping addresses  
- Advanced product search and filtering (by price, rating, brand, etc.)  
- Product tags and highlights (e.g., "New", "Hot", "Sale")  
- Related products and "Frequently Bought Together" suggestions  

### 📊 Admin Tools & Analytics
- Interactive admin dashboard with sales analytics  
- Bulk editing capabilities for products in the admin panel  
- Discount code and promotional offer system  

### 🌐 Site Management & Content
- Multi-language support for international users  
- Multi-currency support with automatic conversion  
- Static pages (About Us, Terms of Service, Privacy Policy, etc.)

### 🚚 Shipping & Order Management
- Region-based shipping cost calculations
  
### 🛡️ Security & Performance Improvements
- API authentication with JWT or OAuth2  
- Rate limiting and throttling for API endpoints  
- Redis-based caching for products and categories  
- Admin activity logging for enhanced security and monitoring  

---

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Bootstrap
- **Asynchronous Tasks:** Celery with Redis
- **Testing:** Pytest

---

## ⚙️ Getting Started from Scratch

### 🔵 Step 1: Install Python

#### Windows:
- Download and install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

#### Linux (Debian-based):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 🟣 Step 2: Install PostgreSQL

#### Windows:
- Download and install from [PostgreSQL.org](https://www.postgresql.org/download/windows/)
- During setup, remember the username and password

#### Linux:
```bash
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

Create a new database and user:
```bash
sudo -u postgres psql
CREATE DATABASE trader_db;
CREATE USER trader_user WITH PASSWORD 'yourpassword';
ALTER ROLE trader_user SET client_encoding TO 'utf8';
ALTER ROLE trader_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE trader_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE trader_db TO trader_user;
\q
```

### 🟢 Step 3: Clone and Setup Project

```bash
mkdir project
cd project
python -m venv .
.\Scripts\activate     # On Windows
# or
source ./bin/activate    # On Linux/macOS
mkdir src
cd src
git clone https://github.com/AhmedHashim04/Django-Ecommerce.git .

pip install -r requirements.txt
```

### 🔵 Step 4: Configure `.env` or `settings.py`
Add your database credentials and environment settings.

### 🟣 Step 5: Run Migrations & Start Project

```bash
python manage.py migrate
python manage.py runserver
```

### 🟡 Step 6: Start Redis & Celery

Make sure Redis is running:

#### Linux:
```bash
sudo apt install redis
sudo service redis start
```

Start Celery:
```bash
celery -A trader worker -l info
```

---

## 🧪 Run Tests

```bash
pytest
```

---

## 🖼️ Screenshots

> _UI screenshots and GIFs below to showcase the frontend._

- ![Homepage](screenshots/homepage.png)
- ![Product Detail](screenshots/product-detail.png)
- ![Cart](screenshots/cart.png)
- ![Checkout](screenshots/checkout.png)
- ![Admin Panel](screenshots/admin.png)

---

## 📁 Project Structure (simplified)

```bash
project/
├── account/
├── cart/
├── contact/
├── order/
├── product/
├── payment/
├── templates/
├── static/
├── project/  # main settings
├── settings/  # main settings
├── manage.py
└── README.md
```

---

## 👤 Author

**Ahmed Hashim**  
[GitHub: AhmedHashim04](https://github.com/AhmedHashim04)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
