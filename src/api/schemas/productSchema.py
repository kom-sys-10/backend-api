from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    price: int
