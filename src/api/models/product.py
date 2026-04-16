from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.dbConnection import Base

class Product(Base):
    __tablename__ = "products"

    pid = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    description = Column(String(100))

    orderitem = relationship("OrderItem", back_populates="product")

   