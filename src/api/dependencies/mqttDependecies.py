"""
FastAPI dependency that provides the shared MQTT client.

Creates a single MqttClient instance at module load time and returns it via
`get_mqtt_client` so every request that needs MQTT access gets the same
connected client.
"""
from mqtt.mqtt import MqttClient

mqtt_client = MqttClient(client_id="fastapi-mqtt")
mqtt_client.connect()


def get_mqtt_client():
    return mqtt_client