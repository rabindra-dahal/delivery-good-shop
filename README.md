# 🛒 Shopkeeper-Customer Modular Order Management System

A modular, production-ready **FastAPI** application designed for local shopkeepers to manage product inventory (rice, noodles, eggs, gas, etc.) and handle incoming customer orders. 

---

## ✨ Features

- **Split Roles**: Distinct workflows for **Shopkeepers** (inventory management, order accept/reject queues) and **Registered Customers** (cart system, checkout history, paginated timelines).
- **Public Browsing**: Unregistered users can view the product catalog and real-time stock levels but cannot add items to the cart or checkout.
- **Modern Security**: Handled via direct `bcrypt` password hashing and secure `PyJWT` authentication.
- **SQLAlchemy 2.0 Unified Mapping**: Built using modern type-annotated `Mapped[...]` and `mapped_column` declarations.
- **Paginated Timeline Engine**: Multi-column sorting (`created_at` DESC, `id` DESC) with `limit` and `offset` constraints to prevent memory strain.
- **Automated Testing Suite**: Includes complete integration test coverage with isolated, in-memory SQLite instances via `pytest`.

---

## 📂 Directory Structure

```text
delivery-good-shop/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # App initialization & router mounting
│   ├── config.py               # 📍 Central environment configurations (Self-contained)
│   ├── database.py             # SQLAlchemy Engine & Session setup
│   ├── models.py               # Modern SQLAlchemy 2.0 database models
│   ├── schemas.py              # Pydantic V2 data validation schemas
│   ├── auth.py                 # Timezone-aware JWT & encryption engine
│   │
│   ├── routes/                 # Specialized endpoint layers
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Registration & Login endpoints
│   │   ├── product_routes.py   # Inventory management endpoints
│   │   ├── cart_routes.py      # Shopping cart workflow endpoints
│   │   └── order_routes.py     # Paginated checkouts & approval hooks
│   │
│   └── services/
│       └── notification.py     # Dispatched client status log alerts
│
├── tests/                      # Automated test suite
│   ├── test_stock_checkout.py  # Stock inventory deduction tests
│   └── test_pagination.py      # Limit/Offset query assertion tests
│
├── seed.py                     # Mock store database populator script
├── Dockerfile                  # Multi-stage optimized builder file
├── docker-compose.yml          # Container environment compose script
├── pytest.ini                  # Pytest orchestration filters
└── requirements.txt            # Frozen dependency manifest
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your local environment.

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone the repository and enter the directory
cd delivery-good-shop

# Initialize virtual environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\activate

# Activate the environment (Mac/Linux)
source venv/bin/activate

# Install all standard required dependencies
pip install -r requirements.txt
```

### 3. Seed Database State
Populate your local SQLite instance with an administrative shopkeeper profile, test customer, and standard stock items (rice, noodles, eggs, gas):
```bash
python seed.py
```
* **Default Shopkeeper Credentials:** Username: `admin_shopkeeper` | Password: `ShopSecret2026!`
* **Default Customer Credentials:** Username: `john_customer` | Password: `CustomerPass123`

### 4. Boot Up the Server
```bash
uvicorn app.main:app --reload
```
Once initialized, visit the interactive Swagger API interface at **[http://127.0.0](http://127.0.0)**.

---

## 🧪 Running Automated Tests

Run the complete integration suite to test stock workflows and pagination logic:
```bash
python -m pytest -v -s
```

---

## 🐳 Docker Container Deployment

### Local Multi-Container Run (Docker Compose)
To stand up the application container and mount a local, persistent data volume folder to host your `shop.db` securely, run:
```bash
# Start up the environment in detached background mode
docker-compose up -d

# Check live logs stream
docker-compose logs -f

# Spin down the active service containers
docker-compose down
```
