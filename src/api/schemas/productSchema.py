"""
Pydantic schemas for product request bodies.

- CreateProductRequest — payload for POST /api/product/
"""
from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    price: int
