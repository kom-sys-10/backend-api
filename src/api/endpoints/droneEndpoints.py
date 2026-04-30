"""
Drone endpoints — /api/drone

GET /checkout-availability - Returns whether weather conditions are acceptable
                             and at least one drone is available for a new delivery.
                             Used by the frontend before showing the checkout flow.
"""
from fastapi import APIRouter, Depends, Response
from services.droneService import DroneService
from dependencies.droneDependecies import get_drone_service
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/drone")
DroneServiceDep = Annotated[DroneService, Depends(get_drone_service)]

@router.get("/checkout-availability")
def get_checkout_availability(drone_service: DroneServiceDep):
    result = drone_service.has_checkout_availability()
    return JSONResponse(content=result, status_code=200)