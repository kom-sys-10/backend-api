"""
SQLAlchemy model for the `drone` table.

Represents a single drone in the fleet. `isAvailable` is derived from
status and maintenance state and is kept in sync by DroneService whenever
a live MQTT report is received.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database.dbConnection import Base

class Drone(Base):
    __tablename__ = "drone"
    did = Column(Integer, primary_key=True, index=True)
    status = Column(String(100), default="idle")
    batteryLevel = Column(Integer, default=100)
    isAvailable = Column(Boolean, default=True)
    isInMaintenance = Column(Boolean, default=False)
    currentOrderId = Column(Integer, ForeignKey("orders.oid"), nullable=True)
