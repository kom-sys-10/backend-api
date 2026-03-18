from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.dbConnection import Base

class Order(Base):
    __tablename__ = "orders"
    
    oid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("users.uid"), nullable=False)

    user = relationship("User", back_populates="orders")
    orderitem = relationship("OrderItem", back_populates="order")
    
