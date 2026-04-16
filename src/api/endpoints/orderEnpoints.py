from fastapi import APIRouter, Depends, Response
from services.orderService import OrderService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from dependencies.orderDependecies import get_order_service
from schemas.orderSchema import CreateOrderRequest, GetOrderResponse

router = APIRouter(prefix="/api/order")
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]

@router.get("/{oid}")
def get_order_by_id(oid: int, orderService: OrderServiceDep):
    order = orderService.get_order_by_id(oid)

    if not order:
        return Response(status_code=204)

    response_body = GetOrderResponse(
        oid=order.oid,
        uid=order.uid,
        date=order.date,
        status=order.status,
        packageWeight=order.packageWeight,
        shipmentType=order.shipmentType,
        address=order.address,
        deliveryDate=order.deliveryDate,
        paymentNumber=order.paymentNumber,
        pids=[item.pid for item in order.orderitem]
    )

    return JSONResponse(
        content=jsonable_encoder(response_body),
        status_code=200
    )

@router.get("/user-order/{uid}")
def get_orders_by_user_id(uid: int, orderService: OrderServiceDep):
    orders = orderService.get_orders_by_user_id(uid)
    if not orders:
        return Response(
            status_code = 204
        )
    return JSONResponse(
        content = jsonable_encoder(orders),
        status_code = 200
    )

@router.post("/")
def create_order(body: CreateOrderRequest, orderService: OrderServiceDep):
    order = orderService.create_order(
        body.uid,
        body.date,
        body.status,
        body.packageWeight,
        body.shipmentType,
        body.address,
        body.deliveryDate,
        body.paymentNumber,
        body.pids
    )
    if not order:
        return JSONResponse(
            content=jsonable_encoder({"msg": "Failed to create order"}),
            status_code=400
        )
    return JSONResponse(
        content=jsonable_encoder(order),
        status_code=201
    )