from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.dbConnection import Base

class Order(Base):
    __tablename__ = "orders"
    
    oid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("users.uid"), nullable=False)
    date = Column(String(100))
    status = Column(String(100))
    packageWeight = Column(Float)
    shipmentType = Column(String(100))
    deliveryDate = Column(String(100))
    address = Column(String(100))
    paymentNumber = Column(String(100))


    user = relationship("User", back_populates="orders")
    orderitem = relationship("OrderItem", back_populates="order")
    
