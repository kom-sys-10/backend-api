# KOM-SYS — Drone Delivery Order Management System

A backend API for managing orders, products, users, and a drone fleet. The system automates the full delivery pipeline from order placement to drone dispatch, using MQTT for real-time drone communication.

## Tech Stack

- **API:** FastAPI (Python 3.11)
- **Database:** MySQL via SQLAlchemy (PyMySQL)
- **Messaging:** MQTT (Paho)
- **Server:** Uvicorn
- **Container:** Docker

---

## Project Structure

```
kom-sys/
├── api/
│   └── backend-api/
│       └── src/api/        # FastAPI application
│           ├── endpoints/  # Route handlers
│           ├── services/   # Business logic
│           ├── models/     # SQLAlchemy models
│           ├── schemas/    # Pydantic schemas
│           ├── jobs/       # Background threads
│           ├── mqtt/       # MQTT client
│           └── database/   # DB connection
└── stm/                    # Legacy state machine components
```

---

## Prerequisites

Before running the API you need two external services available:

- **MySQL** database
- **MQTT broker** (e.g. Mosquitto)

---

## Environment Variables

The application expects the following environment variables. Create a `.env` file or pass them directly to Docker:

```env
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:3306/<dbname>
MQTT_HOST=<mqtt-broker-host>
MQTT_PORT=1883
FRONTEND_URL=http://localhost:5173
```

> The database tables are created automatically on first startup.

---

## Running with Docker

### Build the image

```bash
docker build -t kom-sys-api ./api/backend-api/src/api
```

### Run the container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=mysql+pymysql://user:password@host:3306/komsys \
  -e MQTT_HOST=172.17.0.1 \
  -e MQTT_PORT=1883 \
  -e FRONTEND_URL=http://localhost:5173 \
  --name kom-sys-api \
  kom-sys-api
```

> If your MQTT broker and MySQL are running on the Docker host machine, use `172.17.0.1` as the host (the default Docker bridge gateway).

The API will be available at: `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## API Endpoints

### Users — `/api/user`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/user/` | Get all users |
| GET | `/api/user/{uid}` | Get user by ID |
| POST | `/api/user/` | Create a new user |
| POST | `/api/user/login` | Login |

### Products — `/api/product`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/product/` | Get all products |
| GET | `/api/product/{pid}` | Get product by ID |
| POST | `/api/product/` | Create a new product |

### Orders — `/api/order`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/order/{oid}` | Get order by ID |
| GET | `/api/order/user-order/{uid}` | Get all orders for a user |
| POST | `/api/order/` | Create a new order |

### Drones — `/api/drone`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/drone/checkout-availability` | Check if a drone is available for delivery |

---

## How the Automation Works

Two background threads run automatically when the API starts:

1. **Order status updater** (every 30 seconds) — moves orders through the pipeline:
   `Order placed` → `Order confirmed` → `Packing items`

2. **Dispatch job** (every 60 seconds) — checks orders that are packed and have a drone assigned. If the drone is available, not in maintenance, and has battery above 20%, it sends a `fetch_order` command over MQTT and transitions the order to `Ready for dispatch`.

### MQTT Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `drones/+/status` | Subscribed | Receive drone status updates |
| `drones/{id}/command` | Published | Send commands to a drone |

---

## Database Models

- **users** — user accounts
- **products** — product catalogue
- **orders** — customer orders with status tracking
- **orderitem** — line items linking orders to products
- **drone** — drone fleet with status, battery, and availability

---

## Frontend

The API is configured to accept requests from a frontend running at `http://localhost:5173` (Vite dev server). Update the `FRONTEND_URL` environment variable if your frontend runs on a different origin.
