# tests/test_pagination.py
import os
import sys

# Append the project root folder to Python's search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.main import app
from app.database import get_db
from app.auth import hash_password

# Setup isolated in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_order_history_pagination_logic(client, db_session):
    # ---- STEP 1: Create a customer account ----
    hashed_pass = hash_password("Password123")
    test_user = models.User(username="page_test_user", hashed_password=hashed_pass, role="customer")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # ---- STEP 2: Seed 15 unique dummy orders for this user ----
    for i in range(1, 16):
        dummy_order = models.Order(
            user_id=test_user.id,
            delivery_location=f"Location Address {i}",
            delivery_date=f"2026-10-{i:02d}",
            payment_method="SITE",
            total_amount=100.0 * i,
            status="ACCEPTED" if i % 2 == 0 else "PENDING"
        )
        db_session.add(dummy_order)
    db_session.commit()

    # ---- STEP 3: Authenticate to get a bearer token ----
    login_response = client.post("/auth/login", data={"username": "page_test_user", "password": "Password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ---- STEP 4: Test Page 1 (Limit=10, Offset=0) ----
    # Expecting 10 newest orders out of the 15 total items
    page_1_response = client.get("/orders/history?limit=10&offset=0", headers=headers)
    assert page_1_response.status_code == 200
    page_1_data = page_1_response.json()
    assert len(page_1_data) == 10
    
    # Since we order by created_at DESC, the first element should be the last added (15th order)
    assert page_1_data[0]["delivery_location"] == "Location Address 15"

    # ---- STEP 5: Test Page 2 (Limit=10, Offset=10) ----
    # Expecting the remaining 5 oldest orders
    page_2_response = client.get("/orders/history?limit=10&offset=10", headers=headers)
    assert page_2_response.status_code == 200
    page_2_data = page_2_response.json()
    assert len(page_2_data) == 5
    
    # The last element of page 2 should be the very first historical order seeded
    assert page_2_data[-1]["delivery_location"] == "Location Address 1"

    # ---- STEP 6: Test Max Validation Guard Rails ----
    # Query validation should cap out payload sizes if the client attempts to ask for limit=101
    bad_limit_response = client.get("/orders/history?limit=101&offset=0", headers=headers)
    assert bad_limit_response.status_code == 422  # Pydantic validation error
    
    print("\n✅ Automated Pagination & Page Splitting Logic Passed Successfully!")
