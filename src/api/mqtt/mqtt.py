"""
MQTT client wrapper for drone communication.

Wraps the Paho MQTT library and provides two main communication patterns:
- Fire-and-forget commands via `send_command`.
- Request/response status queries via `request_drone_status`, which sends a
  get_status command and blocks until the drone replies (or times out).

Subscribes to `drones/+/status` on connect and routes incoming messages to
whatever handler is registered via `set_message_handler`.
"""
import json
import logging
import paho.mqtt.client as mqtt
import threading

logger = logging.getLogger(__name__)

MQTT_HOST ="172.17.0.1"
MQTT_PORT = 1883


class MqttClient:
    def __init__(
        self,
        client_id: str,
        host: str = MQTT_HOST,
        port: int = MQTT_PORT
    ):
        self.client = mqtt.Client(client_id=client_id)
        self.host = host
        self.port = port
        self.message_handler = None
        self.status_events: dict[int, threading.Event] = {}
        self.status_responses: dict[int, dict] = {}
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def set_message_handler(self, handler):
        self.message_handler = handler

    def connect(self):
        try:
            print(f"TRYING MQTT CONNECT TO {self.host}:{self.port}")
            self.client.connect(self.host, self.port)
            self.client.loop_start()
            print("MQTT CONNECT CALL SUCCEEDED")
            logger.info("Connecting to MQTT broker at %s:%d", self.host, self.port)
        except Exception as e:
            print(f"MQTT CONNECT FAILED: {e}")
            logger.error("Error connecting to MQTT broker: %s", e)

    def disconnect(self):
        logger.info("Disconnecting from MQTT broker at %s:%d", self.host, self.port)
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, _userdata, flags, reason_code, properties=None):
        print(f"MQTT ON_CONNECT CALLED, reason_code={reason_code}")
        if reason_code == 0:
            print("MQTT CONNECTED OK")
            logger.info("Connected to broker successfully")
            self.client.subscribe("drones/+/status", qos=1)
            print("MQTT SUBSCRIBED TO TOPICS")
            logger.info("Subscribed to drone command and drone_status")
        else:
            print(f"MQTT CONNECTION FAILED, code={reason_code}")
            logger.error("Connection failed with code %s", reason_code)

    def on_disconnect(self, client, _userdata, reason_code, properties=None, *args):
        logger.warning("Disconnected from broker (code=%s)", reason_code)
   
    def on_message(self, client, _userdata, msg):
        """
        Called by Paho for every incoming message.

        Parses the JSON payload, extracts the drone ID from the topic
        (`drones/{id}/status`), stores the response and unblocks any
        `request_drone_status` call that is waiting for that drone, then
        forwards the message to the registered handler (DroneJobs).
        """
        try:
            payload = json.loads(msg.payload.decode())
            print(f"MQTT MESSAGE RECEIVED topic={msg.topic} payload={payload}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON on topic %s: %s", msg.topic, msg.payload)
            return

        parts = msg.topic.split("/")
        if len(parts) >= 3 and parts[0] == "drones" and parts[2] == "status":
            drone_id = int(parts[1])
            self.status_responses[drone_id] = payload
            print(f"Stored status response for drone {drone_id}")

            if drone_id in self.status_events:
                print(f"Setting event for drone {drone_id}")
                self.status_events[drone_id].set()

        if self.message_handler:
            self.message_handler(msg.topic, payload)

    
    #Funksjoner for sjølve sendinga

    def send_command(self, drone_id: int, action: str, data: dict | None = None):
        topic = f"drones/{drone_id}/command"
        payload = {
            "type": "command",
            "action": action,
            "data": data or {}
        }

        result = self.client.publish(topic, json.dumps(payload), qos=1)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("Sent command to drone %d", drone_id)
        else:
            logger.error("Failed to send command to drone %d", drone_id)

    def request_drone_status(self, drone_id: int, timeout: float = 3.0) -> dict | None:
        """
        Sends a get_status command to a drone and waits for its reply.

        Uses a threading.Event to block until the drone's status message
        arrives on `drones/{drone_id}/status`. Returns the parsed payload
        dict, or None if the drone does not respond within `timeout` seconds.
        """
        event = threading.Event()
        self.status_events[drone_id] = event
        print(f"Requesting status for drone {drone_id}")

        try:
            self.send_command(drone_id, "get_status")
            received = event.wait(timeout)
            print(f"Wait result for drone {drone_id}: {received}")

            if not received:
                print(f"Timed out waiting for drone {drone_id}")
                return None

            response = self.status_responses.get(drone_id)
            print(f"Returning response for drone {drone_id}: {response}")
            return response
        finally:
            self.status_events.pop(drone_id, None)