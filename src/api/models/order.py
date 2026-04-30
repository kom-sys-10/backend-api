"""
SQLAlchemy model for the `orders` table.

Tracks the full lifecycle of a delivery order: from placement through packing,
drone transit, and delivery. `dispatchNotified` is set to True once the
dispatch MQTT command has been sent so the job does not send it twice.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
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
    dispatchNotified = Column(Boolean, default=False)
    assignedDroneId = Column(Integer, ForeignKey("drone.did"), nullable=True)


    user = relationship("User", back_populates="orders")
    orderitem = relationship("OrderItem", back_populates="order")
    
