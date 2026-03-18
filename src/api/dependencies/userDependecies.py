from fastapi import Depends
from sqlalchemy.orm import Session
from database.dbConnection import get_db
from services.userService import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
