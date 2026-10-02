# delivery-good-shop
Shop to help shopkeeper manage his business

uvicorn app.main:app --reload


shop_app/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Initializes FastAPI and includes all routers
│   │
│   ├── database.py             # Database connection and session setup
│   ├── models.py               # SQLAlchemy models (User, Product, Cart, Order)
│   ├── schemas.py              # Pydantic schemas for request/response validation
│   ├── auth.py                 # JWT token generation and user authentication
│   │
│   ├── routes/                 # 📂 Split route modules
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Registration and Login endpoints
│   │   ├── product_routes.py   # Stock management and view items endpoints
│   │   ├── cart_routes.py      # 📍 Active: Add to cart, view cart endpoints
│   │   └── order_routes.py     # 📍 Active: Checkout, accept/reject, notifications
│   │
│   └── services/               # (Optional) Core business logic / notifications
│       └── notification.py     # Mock service to alert customers
