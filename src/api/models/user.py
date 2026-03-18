from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.dbConnection import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True)
    name = Column(String(100))
    password = Column(String(100))

    orders = relationship("Order", back_populates="user")