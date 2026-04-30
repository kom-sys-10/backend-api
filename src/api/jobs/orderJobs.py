"""
Background jobs for order pipeline automation.

Two long-running functions are started as daemon threads on app startup:

- `autUpdateOrderStatus`: polls the DB every 30 seconds and advances orders
  through the early pipeline stages (placed → confirmed → packing).
- `dispatch_ready_orders`: polls every 60 seconds and sends `fetch_order`
  MQTT commands to drones for orders that are packed and ready to go.
"""
import time

from database.dbConnection import get_db
from services.orderService import OrderService
from services.droneService import DroneService
from mqtt.mqtt import MqttClient

mqtt_client = MqttClient("order-service")
mqtt_client.connect()


def autUpdateOrderStatus(intervalMinutes: int = 1):
    while True:
        db_generator = get_db()
        db = next(db_generator)

        try:
            service = OrderService(db)
            orders = service.get_all_orders_with_fronted_status()

            for order in orders:
                service.chooseNewOrderStatus(order.oid)

        finally:
            db.close()

        time.sleep(intervalMinutes * 30)


#def notify_orders_ready_for_dispatch(intervalMinutes: int = 1):
    #while True:
        #db_generator = get_db()
        #db = next(db_generator)

        #try:
            #service = OrderService(db)
            #orders = service.get_orders_ready_for_dispatch_notification()

            #for order in orders:
                #payload = {
                    #"oid": order.oid,
                    #"status": order.status
                #}
                #service.mark_dispatch_notification_sent(order.oid)

        #finally:
            #db.close()

        #time.sleep(intervalMinutes * 10)


def dispatch_ready_orders(intervalMinutes: int = 1):
    """
    Sends dispatch commands to drones for orders that are ready to ship.

    Every 60 seconds, fetches orders in "Packing items" status with an assigned
    drone. For each order it checks that the drone is not in maintenance and has
    sufficient battery (>20%). If battery is low, it sends a charge command
    instead. Otherwise it sends a `fetch_order` MQTT command with the delivery
    payload, marks the order as dispatch-notified, and transitions it to
    "Ready for dispatch".
    """
    while True:
        db_generator = get_db()
        db = next(db_generator)

        try:
            order_service = OrderService(db)
            drone_service = DroneService(db, mqtt_client)

            orders = order_service.get_orders_ready_for_dispatch()

            for order in orders:
                if order.assignedDroneId is None:
                    continue

                drone = drone_service.getDroneById(order.assignedDroneId)
                if not drone:
                    continue

                if drone.isInMaintenance:
                    continue

                if drone.status not in ["assigned", "idle"]:
                    continue

                if drone.batteryLevel <= 20:
                    drone_service.updateDroneStatus(drone.did, "charging")
                    drone_service.setDroneAvailable(drone.did, False)
                    mqtt_client.send_command(drone.did, "charge")
                    continue

                payload = {
                    "oid": order.oid,
                    "uid": order.uid,
                    "address": order.address,
                    "deliveryDate": str(order.deliveryDate),
                    "packageWeight": order.packageWeight,
                    "shipmentType": order.shipmentType
                }

                mqtt_client.send_command(drone.did, "fetch_order", payload)

                order_service.mark_dispatch_notification_sent(order.oid)
                order_service.updateOrderStatus(order.oid, "Ready for dispatch")

        finally:
            db.close()

        time.sleep(intervalMinutes * 60)