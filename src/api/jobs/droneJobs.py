"""
MQTT message handler for incoming drone status updates.

DroneJobs is registered as the message handler on the MqttClient. Every
status message published by a drone triggers `handle_drone_message`, which
maps the reported status to the appropriate drone and order state transitions
in the database.
"""
from database.dbConnection import get_db
from services.droneService import DroneService
from services.orderService import OrderService
import threading


class DroneJobs:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def handle_drone_message(self, topic: str, payload: dict):
        """
        Processes a single MQTT message from a drone.

        Extracts the drone ID from the topic (`drones/{id}/status`) and
        dispatches to the correct service method based on the `status` field:

        - charging_complete  → mark drone idle with updated battery
        - maintenance        → mark drone in maintenance
        - maintenance_complete → clear maintenance flag
        - damaged            → mark drone damaged
        - in_transit         → update drone and linked order to "In drone transit"
        - delivery_complete  → mark drone idle, update order to "Delivered"
        - idle               → mark drone idle; send charge command if battery <= 20%

        Opens and closes its own DB session so it is safe to call from the
        MQTT network thread.
        """
        parts = topic.split("/")
        drone_id = int(parts[1])

        db_generator = get_db()
        db = next(db_generator)

        try:
            drone_service = DroneService(db, self.mqtt_client)
            order_service = OrderService(db)

            battery_level = payload.get("batteryLevel")
            status = payload.get("status")
            oid = payload.get("oid")

            if battery_level is not None:
                drone_service.updateDroneBatteryLevel(drone_id, battery_level)

            if status == "charging_complete":
                drone_service.markDroneChargingComplete(drone_id, battery_level or 100)

            elif status == "maintenance":
                drone_service.markDroneMaintenance(drone_id)

            elif status == "maintenance_complete":
                drone_service.clearDroneMaintenance(drone_id)

            elif status == "damaged":
                drone_service.markDroneDamaged(drone_id)

            elif status == "in_transit":
                drone_service.updateDroneStatus(drone_id, "In drone transit")
                drone = drone_service.getDroneById(drone_id)
                order_id = oid or (drone.currentOrderId if drone else None)
                if order_id is not None:
                    order_service.updateOrderStatus(order_id, "In drone transit")

            elif status == "delivery_complete":
                drone = drone_service.getDroneById(drone_id)
                order_id = oid or (drone.currentOrderId if drone else None)
                drone_service.markDroneIdle(drone_id)
                if order_id is not None:
                    order_service.updateOrderStatus(order_id, "Delivered")

            elif status == "idle":
                drone_service.markDroneIdle(drone_id)
            
            if status == "idle" and battery_level is not None and battery_level <= 20:
                print(f"[DroneJobs] Battery low on drone {drone_id} ({battery_level}%) — sending charge")
                threading.Thread(
                    target=self.mqtt_client.send_command,
                    args=(drone_id, "charge"),
                    daemon=True
                ).start()

        finally:
            db.close()