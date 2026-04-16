from sqlalchemy.orm import Session, joinedload
from models.order import Order
from models.product import Product
from models.orderItem import OrderItem
from typing  import Optional, List
from database.dbConnection import get_db
from dependencies.productDependecies import get_product_service


#@singleton
class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_order_by_id(self, oid: int) -> Optional[Order]:
        order = (
            self.db.query(Order)
            .options(
                joinedload(Order.orderitem).joinedload(OrderItem.product)
            )
            .filter(Order.oid == oid)
            .first()
        )
        return order

    def get_orders_by_user_id(self, uid:int) -> Optional[List[Order]]:
        return self.db.query(Order).filter(Order.uid == uid).all()

    def create_order(
        self,
        uid: int,
        date: str,
        status: str,
        packageWeight: float,
        shipmentType: str,
        address: str,
        deliveryDate: str,
        paymentNumber: str,
        pids: List[int]
    ) -> Order:
        order = Order(
            uid=uid,
            date=date,
            status=status,
            packageWeight=packageWeight,
            shipmentType=shipmentType,
            address=address,
            deliveryDate=deliveryDate,
            paymentNumber=paymentNumber,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        for pid in pids:
            item = OrderItem(oid=order.oid, pid=pid)
            self.db.add(item)

        self.db.commit()
        return order

        