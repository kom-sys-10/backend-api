"""
Business logic for order management.

Handles order creation (including attaching order items), status transitions
through the pipeline, and querying orders that are ready for drone dispatch.
"""
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from models.order import Order
from models.orderItem import OrderItem


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_order_by_id(self, oid: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.orderitem).joinedload(OrderItem.product)
            )
            .filter(Order.oid == oid)
            .first()
        )

    def get_orders_by_user_id(self, uid: int) -> List[Order]:
        return self.db.query(Order).filter(Order.uid == uid).all()

    def create_order(
        # Creates the order row, commits it to get its ID, then attaches all
        # order items in a second commit.
        self,
        uid: int,
        date: str,
        status: str,
        packageWeight: float,
        shipmentType: str,
        address: str,
        deliveryDate: str,
        paymentNumber: str,
        droneId: Optional[int],
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
            dispatchNotified=False,
            assignedDroneId=droneId,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        for pid in pids:
            item = OrderItem(oid=order.oid, pid=pid)
            self.db.add(item)

        self.db.commit()
        return order

    def updateOrderStatus(self, oid: int, state: str) -> None:
        order = self.get_order_by_id(oid)
        if order:
            order.status = state
            self.db.commit()

    def get_all_orders_with_fronted_status(self) -> List[Order]:
        orders = (
            self.db.query(Order)
            .filter(Order.status != "Ready for dispatch" 
            or Order.status != "In drone transit"
            or Order.status != "Delivered"
            or Order.status != "Packing items"
            )
        )
        return orders

    def chooseNewOrderStatus(self, oid: int) -> None:
        """
        Advances an order one step through the early pipeline stages.

        Only transitions: Order placed → Order confirmed → Packing items.
        Orders already at later stages are left unchanged.
        """
        newStatus = ""
        currentStatus = (
            self.db.query(Order.status)
            .filter(Order.oid == oid)
            .scalar()
        )

        match currentStatus:
            case "Order placed":
                newStatus = "Order confirmed"
            case "Order confirmed":
                newStatus = "Packing items"

        if newStatus:
            self.updateOrderStatus(oid, newStatus)

    def get_orders_ready_for_dispatch(self) -> List[Order]:
        """
        Returns orders that are packed, have a drone assigned, and haven't
        had the dispatch command sent yet. Used by the dispatch background job.
        """
        return (
            self.db.query(Order)
            .filter(
                Order.status == "Packing items",
                #Order.assignedDroneId != None,
                Order.assignedDroneId is not None,
                Order.dispatchNotified == False
            )
            .all()
        )

    def get_orders_ready_for_dispatch_notification(self) -> List[Order]:
        return (
            self.db.query(Order)
            .filter(
                Order.status == "Packing items",
                Order.dispatchNotified == False
            )
            .all()
        )

    def mark_dispatch_notification_sent(self, oid: int) -> None:
        order = self.get_order_by_id(oid)
        if order:
            order.dispatchNotified = True
            self.db.commit()

    #def assign_order_to_drone(self, oid: int, did: int) -> None:
        #order = self.get_order_by_id(oid)
        #if order:
            #order.assignedDroneId = did
            #order.status = "Ready for dispatch"
            #self.db.commit()