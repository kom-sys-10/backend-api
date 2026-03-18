from fastapi import APIRouter, Depends, Response
from services.userService import UserService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from dependencies.userDependecies import get_user_service
from typing import Annotated
from schemas.userSchema import CreateUserRequest, LoginRequest

router = APIRouter(prefix="/api/user")
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

@router.get("/")
def get_all_user_endpoint(userService: UserServiceDep):
    users = userService.get_all_user()
    if not users:
        return Response(
            status_code = 204
        )
    
    return JSONResponse(
        content = jsonable_encoder(users),
        status_code = 200
    )

@router.get("/{uid}")
def get_user_by_id(userService: UserServiceDep, uid: int):
    user = userService.get_user_by_id(uid)
    if not user:
        return Response(
            status_code = 204
        )
    return JSONResponse(
        content = jsonable_encoder(user),
        status_code = 200
    )

@router.post("/")
def create_user(body: CreateUserRequest, userService: UserServiceDep):
    user = userService.create_user(body.name, body.password)
    if not user:
        return JSONResponse(
            content = jsonable_encoder({"msg": "Failed to create user"}),
            status_code = 400
        )
    return JSONResponse(
        content = jsonable_encoder(user),
        status_code = 201
    )

@router.post("/login")
def login(body: LoginRequest, userService: UserServiceDep):
    user = userService.login(body.name, body.password)
    if not user:
        return JSONResponse(
            content = jsonable_encoder({"msg": "Failed to login"}),
            status_code = 401
        )
    return JSONResponse(
        content = jsonable_encoder(user),
        status_code = 200
    )