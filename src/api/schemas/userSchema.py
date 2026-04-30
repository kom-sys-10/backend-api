"""
Pydantic schemas for user request bodies.

- CreateUserRequest — payload for POST /api/user/
- LoginRequest      — payload for POST /api/user/login
"""
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    password: str

class LoginRequest(BaseModel):
    name: str
    password: str