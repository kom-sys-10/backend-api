"""SQLAlchemy model for the `orderitem` join table linking orders to products."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.dbConnection import Base

class OrderItem(Base):
    __tablename__ = "orderitem"

    oiid = Column(Integer, primary_key=True)
    oid = Column(Integer, ForeignKey("orders.oid"), nullable=False)
    pid = Column(Integer, ForeignKey("products.pid"), nullable=False)

    order = relationship("Order", back_populates="orderitem")
    product = relationship("Product", back_populates="orderitem")