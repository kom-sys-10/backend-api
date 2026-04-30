"""
FastAPI dependency that constructs a DroneService with a DB session and the
shared MQTT client injected from app state.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from database.dbConnection import get_db
from services.droneService import DroneService
from mqtt.mqtt import MqttClient
from dependencies.mqttDependecies import get_mqtt_client


def get_drone_service(
    db: Session = Depends(get_db),
    mqtt_client: MqttClient = Depends(get_mqtt_client)
):
    return DroneService(db, mqtt_client)