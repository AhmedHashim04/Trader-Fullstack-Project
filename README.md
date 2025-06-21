
🛒 Trader - E-commerce Platform

Trader is a full-featured e-commerce platform built with Django and PostgreSQL. Inspired by Noon, it offers complete product and order management, integrated payment systems (including Vodafone Cash), CSV import/export, and a modern responsive frontend using Bootstrap.
🚀 Features

    🧾 Product & Category Management with inventory control

    💳 Secure Payments, including Vodafone Cash integration

    🛍️ Shopping Cart & Order Management

    📊 CSV Import/Export for product data

    ⏱️ Background Tasks using Redis & Celery (e.g., order notifications)

    🎨 Responsive Frontend using Bootstrap, HTML5, and CSS3

    🧪 Test Coverage with Pytest for core functionalities

    💌 Email Notifications for orders, password resets, and promotions

    🧾 Invoices & Order History, including PDF export

    💬 Product Reviews & Ratings

    💚 Wishlist / Favorites System

    👥 User Profiles with multi-address shipping support

    🔎 Advanced Search & Filtering (price, rating, brand, etc.)

    📦 Order Tracking with status updates (Processing → Shipped → Delivered)

    🛍️ Related Products and "Frequently Bought Together" suggestions

    📄 Static Pages (About Us, Terms, Privacy Policy, etc.)

    🚚 Region-Based Shipping Cost Calculations

    ⚡ Redis-Based Caching for products and categories

    🛡️ Admin Activity Logging for enhanced monitoring and security

🚧 Upcoming Features
🧵 Product Variants

    Support for multiple colors, sizes, and other attributes

⚖️ Shipping Weight Calculations

    Dynamic shipping cost based on product weight

📊 Admin Tools & Analytics

    Interactive dashboard with sales analytics

    Bulk product editing in admin panel

    Discount code and promotional offer system

🌐 Internationalization & Localization

    Multi-language support

    Multi-currency support with real-time conversion

🛡️ Security & Performance

    API authentication using JWT or OAuth2

    Rate limiting & throttling for public APIs

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JS, Bootstrap
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
git clone https://github.com/AhmedHashim04/Trader-Fullstack-Project.git .

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
