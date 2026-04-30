"""
Database connection and session management.

Provides the SQLAlchemy engine, session factory, and declarative base used
by all models. Also exposes `get_db`, a generator dependency that opens a
session for a request and closes it when the request is done.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "mysql+pymysql://dbuser:dbpassword123@16.171.145.191:3306/komsys"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()