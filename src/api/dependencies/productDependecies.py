from fastapi import Depends
from sqlalchemy.orm import Session
from database.dbConnection import get_db
from services.productService import ProductService

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)
