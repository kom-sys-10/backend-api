"""
Business logic for drone fleet management.

Handles all drone state transitions (idle, assigned, charging, maintenance,
damaged), syncing drone state from live MQTT status reports, and selecting
an available drone for a new order. Also contains the weather check that
gates checkout availability.
"""
import random
from typing import Optional, List
from sqlalchemy.orm import Session
from models.drone import Drone
from mqtt.mqtt import MqttClient


class DroneService:
    def __init__(self, db: Session, mqtt_client: Optional[MqttClient] = None):
        self.db = db
        self.mqtt_client = mqtt_client

    def getDroneById(self, did: int) -> Optional[Drone]:
        return self.db.query(Drone).filter(Drone.did == did).first()

    def updateDroneStatus(self, did: int, status: str) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.status = status
            self.db.commit()

    def updateDroneBatteryLevel(self, did: int, batteryLevel: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.batteryLevel = batteryLevel
            self.db.commit()

    def setDroneAvailable(self, did: int, is_available: bool) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.isAvailable = is_available
            self.db.commit()

    def setDroneMaintenance(self, did: int, is_in_maintenance: bool) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.isInMaintenance = is_in_maintenance
            self.db.commit()

    def setCurrentOrder(self, did: int, oid: Optional[int]) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.currentOrderId = oid
            self.db.commit()

    def checkWeather(self) -> bool:
        random_number = random.randint(1, 100)
        return random_number > 15

    def get_db_candidate_drones(self) -> List[Drone]:
        return (
            self.db.query(Drone)
            .filter(
                Drone.isAvailable == True,
                Drone.isInMaintenance == False,
                Drone.status == "idle"
            )
            .order_by(Drone.did.asc())
            .all()
        )

    def sync_drone_with_report(self, did: int, report: dict) -> None:
        """
        Updates the DB record for a drone from a live MQTT status report.

        Recalculates `isAvailable` based on status and maintenance flag so the
        DB stays consistent with what the drone is actually reporting.
        """
        drone = self.getDroneById(did)
        if not drone:
            return

        reported_status = report.get("status")
        reported_battery = report.get("batteryLevel")
        reported_maintenance = report.get("isInMaintenance")

        if reported_status is not None:
            drone.status = reported_status

        if reported_battery is not None:
            drone.batteryLevel = reported_battery

        if reported_maintenance is not None:
            drone.isInMaintenance = reported_maintenance

        drone.isAvailable = (
            drone.status == "idle" and
            not bool(drone.isInMaintenance)
        )

        self.db.commit()

    def getFirstConfirmedUsableDrone(self) -> Optional[Drone]:
        """
        Finds the first drone that is confirmed usable via a live MQTT status check.

        Queries the DB for candidate drones (idle, available, not in maintenance),
        then pings each one over MQTT. The DB record is updated with the live report
        before checking conditions, so stale DB state cannot cause a bad assignment.
        Returns the first drone that passes all checks, or None if none respond.
        """
        if not self.mqtt_client:
            return None

        candidates = self.get_db_candidate_drones()

        for drone in candidates:
            report = self.mqtt_client.request_drone_status(drone.did, timeout=20.0)

            if report is None:
                continue

            self.sync_drone_with_report(drone.did, report)

            updated_drone = self.getDroneById(drone.did)
            if not updated_drone:
                continue

            const_drone_status = updated_drone.status == "idle"
            updated_drone_maint = updated_drone.isInMaintenance
            updated_drone_battery = updated_drone.batteryLevel > 20
            updated_drone_isAv = updated_drone.isAvailable

            if (
                updated_drone.status == "idle"
                and not updated_drone.isInMaintenance
                and updated_drone.batteryLevel > 20
                and updated_drone.isAvailable
            ):
                print(f"updated_drone")
                return updated_drone

        print(f"returns None")
        return None

    def has_checkout_availability(self) -> dict:
        weather_ok = self.checkWeather()

        if not weather_ok:
            return {
                "weatherOk": False,
                "droneAvailable": False
            }

        drone = self.getFirstConfirmedUsableDrone()

        return {
            "weatherOk": True,
            "droneAvailable": drone is not None
        }

    def reserveFirstUsableDrone(self) -> Optional[Drone]:
        """
        Finds the first confirmed usable drone and immediately marks it as
        assigned/unavailable so no other order can claim it concurrently.
        """
        drone = self.getFirstConfirmedUsableDrone()
        if not drone:
            return None

        drone.isAvailable = False
        drone.status = "assigned"
        self.db.commit()
        self.db.refresh(drone)
        return drone

    def assignOrderToDrone(self, did: int, oid: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.currentOrderId = oid
            drone.status = "assigned"
            drone.isAvailable = False
            self.db.commit()

    def markDroneIdle(self, did: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.status = "idle"
            drone.isAvailable = True
            drone.currentOrderId = None
            self.db.commit()

    def markDroneChargingComplete(self, did: int, batteryLevel: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.batteryLevel = batteryLevel
            drone.status = "idle"
            drone.isAvailable = True
            self.db.commit()

    def markDroneDamaged(self, did: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.status = "damaged"
            drone.isAvailable = False
            self.db.commit()

    def markDroneMaintenance(self, did: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.status = "maintenance"
            drone.isAvailable = False
            drone.isInMaintenance = True
            self.db.commit()

    def clearDroneMaintenance(self, did: int) -> None:
        drone = self.getDroneById(did)
        if drone:
            drone.status = "idle"
            drone.isAvailable = True
            drone.isInMaintenance = False
            self.db.commit()