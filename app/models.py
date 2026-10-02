# app/models.py
import datetime
from typing import List
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="customer") # "customer" or "shopkeeper"

    # Relationships
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0)

    # Relationships
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    delivery_location: Mapped[str] = mapped_column(String, nullable=False)
    delivery_date: Mapped[str] = mapped_column(String, nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=False) # "SITE" or "BANK_WALLET"
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING") # "PENDING", "ACCEPTED", "REJECTED"
    
    # Timezone-aware UTC timestamp mapping
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
