from sqlalchemy.orm import Session
from models.user import User
from typing import Optional, List
from database.dbConnection import get_db

#@singleton
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, uid: int) -> Optional[User]:
        return self.db.query(User).filter(User.uid == uid).first()
    
    def get_all_user(self) -> List[User]:
        return self.db.query(User).all()

    def create_user(self, name: str, password: str) -> User:
        user = User(name=name, password=password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
        
    def login(self, name: str, password: str) -> User:
        user = self.db.query(User).filter(User.name == name).first()
        if(user.password == password):
            return user
        return None

    