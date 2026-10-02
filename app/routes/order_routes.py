from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user, verify_shopkeeper
from app.services.notification import NotificationService 
from app import models, schemas

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# --- CUSTOMER ENDPOINTS ---

@router.post("/checkout", response_model=schemas.OrderResponse)
def place_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch active items from customer cart
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is completely empty.")

    # Calculate total and double-check physical stock levels
    total_amount = 0.0
    for item in cart_items:
        if item.product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock changed. '{item.product.name}' no longer has requested quantity."
            )
        total_amount += item.product.price * item.quantity

    # Create the pending master order entry
    new_order = models.Order(
        user_id=current_user.id,
        delivery_location=order_in.delivery_location,
        delivery_date=order_in.delivery_date,
        payment_method=order_in.payment_method,
        total_amount=total_amount,
        status="PENDING"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Attach products into individual order items and deduct stock inventory
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )
        # Deduct the stock instantly to avoid overselling
        item.product.stock_quantity -= item.quantity
        db.add(order_item)

    # Clear customer cart out after checkout completes successfully
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    db.refresh(new_order)
    
    return new_order


# --- SHOPKEEPER ENDPOINTS ---

@router.get("/shopkeeper/all", response_model=List[schemas.OrderResponse])
def shopkeeper_view_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(verify_shopkeeper)
):
    # Allows shopkeeper to view all incoming customer orders
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@router.patch("/shopkeeper/{order_id}/process", response_model=schemas.OrderResponse)
def process_order(
    order_id: int,
    action: schemas.OrderProcessAction,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(verify_shopkeeper)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order matching ID not found.")
    
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="This order has already been processed.")

    if action.status == "ACCEPTED":
        order.status = "ACCEPTED"
        # Trigger clean notification service
        NotificationService.send_order_accepted_alert(order, order.user.username)
    
    elif action.status == "REJECTED":
        order.status = "REJECTED"
        # Restock items back since order was canceled
        for item in order.order_items:
            item.product.stock_quantity += item.quantity
        # Trigger clean notification service
        NotificationService.send_order_rejected_alert(order, order.user.username)
    
    db.commit()
    db.refresh(order)
    return order
