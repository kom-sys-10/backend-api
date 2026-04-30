"""
Entry point for the KOM-SYS FastAPI application.

Responsibilities:
- Creates the FastAPI app instance and registers all routers.
- On startup: creates database tables, starts background job threads,
  initialises the MQTT client, and wires up the drone message handler.
- On shutdown: disconnects the MQTT client cleanly.
- Configures CORS to allow requests from the Vite frontend.
"""
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.dbConnection import Base, engine
from models.user import User
from models.product import Product
from models.order import Order
from models.orderItem import OrderItem
from models.drone import Drone

from endpoints.test import router as test_router
from endpoints.userEndpoints import router as user_router
from endpoints.productEndpoints import router as product_router
from endpoints.orderEnpoints import router as order_router
from endpoints.droneEndpoints import router as drone_router

from jobs.orderJobs import autUpdateOrderStatus, dispatch_ready_orders
from jobs.droneJobs import DroneJobs
from mqtt.mqtt import MqttClient


app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    order_thread = threading.Thread(
        target=autUpdateOrderStatus,
        daemon=True
    )
    order_thread.start()

    dispatch_thread = threading.Thread(
        target=dispatch_ready_orders,
        daemon=True
    )
    dispatch_thread.start()

    app.state.mqtt_client = MqttClient(client_id="server")
    app.state.drone_jobs = DroneJobs(app.state.mqtt_client)

    app.state.mqtt_client.set_message_handler(
        app.state.drone_jobs.handle_drone_message
    )
    print("STARTING MQTT CLIENT")
    app.state.mqtt_client.connect()


@app.on_event("shutdown")
def on_shutdown():
    if hasattr(app.state, "mqtt_client"):
        app.state.mqtt_client.disconnect()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(drone_router)