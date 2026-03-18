from fastapi import FastAPI
from endpoints.test import router as test_router
from database.dbConnection import Base, engine
from models.user import User
from models.product import Product
from models.order import Order
from models.orderItem import OrderItem

from endpoints.userEndpoints import router as user_router
from endpoints.productEndpoints import router as product_router
from endpoints.orderEnpoints import router as order_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)



app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)

