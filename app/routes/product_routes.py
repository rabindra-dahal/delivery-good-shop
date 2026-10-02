from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(
    prefix="/products",
    tags=["Products & Stock Inventory"]
)

# --- PUBLIC ACCESS ENDPOINT ---
@router.get("/", response_model=List[schemas.ProductResponse])
def view_all_products(db: Session = Depends(get_db)):
    """
    Open to everyone (Unregistered & Registered).
    Allows viewing names, prices, and seeing if items are in stock.
    """
    return db.query(models.Product).all()


# --- SHOPKEEPER AUTHORIZED ENDPOINT ---
@router.post("/add-stock", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def add_or_update_stock(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.verify_shopkeeper) # Protects endpoint
):
    """
    Restricted to shopkeepers only.
    Adds a new item type or upserts/increases current inventory counts.
    """
    existing_product = db.query(models.Product).filter(models.Product.name == product_in.name).first()
    
    if existing_product:
        # Increment existing stock count if item type already exists
        existing_product.stock_quantity += product_in.stock_quantity
        existing_product.price = product_in.price  # Update to latest pricing if necessary
        db.commit()
        db.refresh(existing_product)
        return existing_product

    # Otherwise, create a totally brand new stock entry
    new_product = models.Product(
        name=product_in.name,
        price=product_in.price,
        stock_quantity=product_in.stock_quantity
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
