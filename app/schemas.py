# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal
from datetime import datetime

# ==========================================
#               AUTH SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")
    role: Literal["customer", "shopkeeper"] = "customer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


# ==========================================
#             PRODUCT SCHEMAS
# ==========================================

class ProductCreate(BaseModel):
    name: str = Field(..., description="Name of the grocery item (e.g., Rice, Gas)")
    price: float = Field(gt=0, description="Price must be a positive number greater than zero")
    stock_quantity: int = Field(ge=0, description="Stock inventory cannot be a negative value")

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
#               CART SCHEMAS
# ==========================================

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity to add must be at least 1 unit")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class CartSummaryItem(BaseModel):
    id: int
    product_name: str
    quantity: int
    price_per_unit: float
    item_total: float


class CartOverviewResponse(BaseModel):
    items: List[CartSummaryItem]
    total_amount: float


# ==========================================
#              ORDER SCHEMAS
# ==========================================

class OrderCreate(BaseModel):
    delivery_location: str = Field(..., description="Complete physical address for the dropshipping route")
    delivery_date: str = Field(..., description="Scheduled delivery timeline requested by the customer")
    payment_method: Literal["SITE", "BANK_WALLET"] = Field(..., description="Choose payment via cash on site or digital bank wallet")


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class OrderProcessAction(BaseModel):
    status: Literal["ACCEPTED", "REJECTED"] = Field(..., description="Action taken by the shopkeeper to accept or cancel the request")
