"""FastAPI dependency that constructs an OrderService with a DB session."""
from fastapi import Depends
from sqlalchemy.orm import Session
from database.dbConnection import get_db
from services.orderService import OrderService

def get_order_service(db: Session = Depends(get_db)):
    return OrderService(db)