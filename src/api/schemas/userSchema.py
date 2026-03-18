from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    password: str

class LoginRequest(BaseModel):
    name: str
    password: str