# tests/test_stock_checkout.py
import os
import sys

# Dynamically append the project root folder to Python's search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. CRITICAL: Import models completely first so SQLAlchemy registers all tables
from app import models  
from app.main import app
from app.database import get_db
from app.auth import hash_password

# 2. Setup isolated in-memory SQLite database
# Note: "check_same_thread=False" and StaticPool are required for multi-threaded in-memory tests
from sqlalchemy.pool import StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database schema with ALL tables before each test."""
    # This now catches cart_items, orders, order_items correctly
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Overrides FastAPI's get_db dependency to point to our testing database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# ... keep your test_checkout_deducts_product_stock_accurately code exactly the same ...



def test_checkout_deducts_product_stock_accurately(client, db_session):
    # ---- STEP 1: Seed a sample product into the database ----
    initial_stock = 50
    ordered_quantity = 5
    
    test_product = models.Product(
        name="Basmati Rice (1kg)",
        price=180.0,
        stock_quantity=initial_stock
    )
    db_session.add(test_product)
    
    # Also create a default customer account so we can log in
    hashed_pass = hash_password("SecurePassword123")
    test_user = models.User(
        username="integration_test_user",
        hashed_password=hashed_pass,
        role="customer"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_product)
    db_session.refresh(test_user)

    # ---- STEP 2: Authenticate and log in the customer via Form Data ----
    login_response = client.post(
        "/auth/login",
        data={"username": "integration_test_user", "password": "SecurePassword123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ---- STEP 3: Add item to the shopping cart ----
    cart_payload = {
        "product_id": test_product.id,
        "quantity": ordered_quantity
    }
    cart_response = client.post("/cart/add", json=cart_payload, headers=headers)
    assert cart_response.status_code == 200

    # ---- STEP 4: Perform Checkout ----
    checkout_payload = {
        "delivery_location": "123 Main Street, Tilottama",
        "delivery_date": "2026-10-05",
        "payment_method": "BANK_WALLET"
    }
    checkout_response = client.post("/orders/checkout", json=checkout_payload, headers=headers)
    assert checkout_response.status_code == 200
    
    # ---- STEP 5: Verify Database Stock Update ----
    # Expel the instance state cache to fetch a completely clean record state from SQLite
    db_session.expire_all()
    
    updated_product = db_session.query(models.Product).filter(models.Product.id == test_product.id).first()
    expected_stock = initial_stock - ordered_quantity
    
    # Assertions to ensure math holds up perfectly across endpoints
    assert updated_product.stock_quantity == expected_stock
    print(f"\n✅ Integration Test Passed! Initial stock: {initial_stock}, Ordered: {ordered_quantity}, Remaining stock: {updated_product.stock_quantity}")
