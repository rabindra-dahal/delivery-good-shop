from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"]
)

@router.post("/add", response_model=schemas.CartItemResponse)
def add_to_cart(
    item_in: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Verify the product exists and is in stock
    product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock_quantity < item_in.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough stock. Only {product.stock_quantity} units available."
        )

    # 2. Check if product already exists in this user's cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item_in.product_id
    ).first()

    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item_in.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(status_code=400, detail="Total requested quantity exceeds stock limits.")
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # 3. Create fresh cart item record
    new_cart_item = models.CartItem(
        user_id=current_user.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item


@router.get("/", response_model=schemas.CartOverviewResponse)
def view_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    
    total_amount = 0.0
    items_summary = []
    
    for item in cart_items:
        item_total = item.product.price * item.quantity
        total_amount += item_total
        items_summary.append({
            "id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price_per_unit": item.product.price,
            "item_total": item_total
        })
        
    return {"items": items_summary, "total_amount": total_amount}
