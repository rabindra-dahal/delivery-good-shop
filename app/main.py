from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import auth_routes, product_routes, cart_routes, order_routes

# Initialize your DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopkeeper-Customer Modular System")

# Register our sub-module routers
app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(cart_routes.router)   # Links cart paths
app.include_router(order_routes.router)  # Links order paths

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "Welcome to the Corner Shop API"}
