"""
Order endpoints — /api/order

GET  /{oid}              - Fetch a single order with its items and drone maintenance status.
GET  /user-order/{uid}   - Fetch all orders belonging to a user.
POST /                   - Create a new order. Auto-assigns the first available DB candidate
                           drone if none is provided in the request body.
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated

from services.orderService import OrderService
from services.droneService import DroneService

from dependencies.orderDependecies import get_order_service
from dependencies.droneDependecies import get_drone_service

from schemas.orderSchema import (
    CreateOrderRequest,
    GetOrderResponse,
    UpdateOrderStatusRequest
)

router = APIRouter(prefix="/api/order")

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
DroneServiceDep = Annotated[DroneService, Depends(get_drone_service)]


@router.get("/{oid}")
def get_order_by_id(oid: int, orderService: OrderServiceDep, droneService: DroneServiceDep):
    order = orderService.get_order_by_id(oid)

    if not order:
        return Response(status_code=204)

    drone_in_maintenance = False
    if order.assignedDroneId is not None:
        drone = droneService.getDroneById(order.assignedDroneId)
        if drone:
            drone_in_maintenance = bool(drone.isInMaintenance)

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
        droneId=order.assignedDroneId,
        pids=[item.pid for item in order.orderitem],
        droneInMaintenance=drone_in_maintenance
    )

    return JSONResponse(
        content=jsonable_encoder(response_body),
        status_code=200
    )


@router.get("/user-order/{uid}")
def get_orders_by_user_id(uid: int, orderService: OrderServiceDep):
    orders = orderService.get_orders_by_user_id(uid)

    if not orders:
        return Response(status_code=204)

    return JSONResponse(
        content=jsonable_encoder(orders),
        status_code=200
    )


@router.post("/")
def create_order(
    body: CreateOrderRequest,
    orderService: OrderServiceDep,
    droneService: DroneServiceDep,
):
    drone_id = body.droneId
    if drone_id is None:
        candidates = droneService.get_db_candidate_drones()
        if candidates:
            drone_id = candidates[0].did

    order = orderService.create_order(
        body.uid,
        body.date,
        body.status,
        body.packageWeight,
        body.shipmentType,
        body.address,
        body.deliveryDate,
        body.paymentNumber,
        drone_id,
        body.pids
    )

    if not order:
        return JSONResponse(
            content=jsonable_encoder({"msg": "Failed to create order"}),
            status_code=400
        )

    if drone_id is not None:
        droneService.assignOrderToDrone(drone_id, order.oid)

    return JSONResponse(
        content=jsonable_encoder({
            "msg": "Order created successfully",
            "order": order,
            "assignedDroneId": drone_id
        }),
        status_code=201
    )