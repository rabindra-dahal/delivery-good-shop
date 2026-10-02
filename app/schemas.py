from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["customer", "shopkeeper"] = "customer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# --- PRODUCT SCHEMAS ---
class ProductCreate(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock_quantity: int = Field(ge=0, description="Stock cannot be negative")

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int

    class Config:
        from_attributes = True


# --- CART SCHEMAS ---
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class CartSummaryItem(BaseModel):
    id: int
    product_name: str
    quantity: int
    price_per_unit: float
    item_total: float

class CartOverviewResponse(BaseModel):
    items: List[CartSummaryItem]
    total_amount: float


# --- ORDER SCHEMAS ---
class OrderCreate(BaseModel):
    delivery_location: str
    delivery_date: str
    payment_method: Literal["SITE", "BANK_WALLET"]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    delivery_location: str
    delivery_date: str
    payment_method: str
    total_amount: float
    status: str
    created_at: datetime
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

class OrderProcessAction(BaseModel):
    status: Literal["ACCEPTED", "REJECTED"]
