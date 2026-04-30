"""
Business logic for product management.

Simple CRUD operations for the product catalogue.
"""
from sqlalchemy.orm import Session
from models.product import Product
from typing  import Optional, List
from database.dbConnection import get_db

#@singleton
class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product_by_id(self, pid: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.pid == pid).first()

    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def create_product(self, name: str, price: int) -> Product:
        product = Product(name=name, price=price)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    