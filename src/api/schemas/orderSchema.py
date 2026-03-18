from pydantic import BaseModel
from typing  import List

class CreateOrderRequest(BaseModel):
    uid: int
    pids: List[int]