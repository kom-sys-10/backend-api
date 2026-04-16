from pydantic import BaseModel
from typing import List

class CreateOrderRequest(BaseModel):
    uid: int
    date: str
    status: str
    packageWeight: float
    shipmentType: str
    address: str
    deliveryDate: str
    paymentNumber: str
    pids: List[int]

class GetOrderResponse(BaseModel):
    oid: int
    uid: int
    date: str
    status: str
    packageWeight: float
    shipmentType: str
    address: str
    deliveryDate: str
    paymentNumber: str
    pids: List[int]