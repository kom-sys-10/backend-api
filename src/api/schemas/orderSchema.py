"""
Pydantic schemas for order request and response bodies.

- CreateOrderRequest  — payload for POST /api/order/
- GetOrderResponse    — response shape for GET /api/order/{oid}, includes
                        drone maintenance status so the frontend can warn the user.
- UpdateOrderStatusRequest — payload for manually updating an order's status.
"""
from pydantic import BaseModel
from typing import List, Optional

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
    droneId: Optional[int] = None

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
    droneId: int
    pids: List[int]
    droneInMaintenance: bool = False

class UpdateOrderStatusRequest(BaseModel):
    oid: int
    state: str