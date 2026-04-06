# NodeTrace Backend

The NodeTrace Backend is the core API server for the NodeTrace monitoring platform. Built with FastAPI, it provides secure device registration, telemetry collection, real-time alerting, and administrative APIs for monitoring device fleets.

## Features

### Authentication & Security
- **JWT-based Admin Authentication**: Secure admin login with bcrypt password hashing
- **Device Token Authentication**: Bearer token authentication for agents
- **Rate Limiting**: Per-device and per-IP rate limiting with SlowAPI
- **Secure Enrollment**: Shared secret key for device registration

### Telemetry & Monitoring
- **Comprehensive Telemetry**: CPU, RAM, disk, network stats, active connections, processes
- **Real-time Alerting**: Automatic alerts for resource thresholds
- **Heartbeat Monitoring**: Device online/offline status tracking
- **Historical Data**: Time-series telemetry storage and retrieval

### API Endpoints
- **Agent APIs**: Registration, telemetry submission, heartbeat
- **Admin APIs**: Device management, alert management, status monitoring
- **RESTful Design**: Clean, documented APIs with OpenAPI/Swagger

### Infrastructure
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Docker Support**: Containerized deployment with docker-compose
- **CORS Enabled**: Ready for frontend integration
- **Environment Configuration**: Secure secret management

## Project Structure

```
app/
├── api/v1/
│   ├── endpoints.py    # Main API endpoints (agents, dashboard, alerts)
│   └── auth.py         # Admin authentication
├── models/
│   ├── device.py       # Device and telemetry models
│   ├── telemetry.py    # Telemetry data model
│   ├── alert.py        # Alert system model
│   └── user.py         # Admin user model
├── schemas/
│   ├── device.py       # Pydantic schemas for API
│   ├── user.py         # User schemas
│   └── alert.py        # Alert schemas
├── utils/
│   ├── security.py     # Device token generation/validation
│   ├── auth.py         # JWT admin authentication
│   ├── ratelimit.py    # Rate limiting configuration
│   └── logger.py       # Logging utilities
├── database/
│   ├── base.py         # SQLAlchemy base
│   └── connection.py   # Database connection
├── core/
│   └── config.py       # Environment configuration
└── main.py             # FastAPI application
```

### Telemetry and Heartbeat
- CPU/RAM usage, local/public IP, geolocation, process list
- Heartbeat check-in and last seen tracking
- Status calculation and history retrieval

### Dashboard Endpoints
- Device list
- Device detail
- Telemetry history
- Online/offline summary

### Security
- CORS configuration
- SlowAPI rate limiting
- JWT and bearer token authentication
- Environment-based secret management

---

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (optional, recommended)

---

## Local Setup (without Docker)

1. Clone repository

```bash
git clone https://github.com/<your-username>/NodeTrace.git
cd NodeTrace/backend-py
```

2. Create Python virtual environment

```bash
python -m venv .venv
. .venv/Scripts/activate   #  For Windows
source .venv/bin/activate  # For macOS/Linux
```

3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configure `.env`

Create `.env` in `backend-py` with:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=nodetrace
DB_PASSWORD=nodetrace_password
DB_NAME=nodetrace_db
ENROLL_KEY=NT-ENROLL-2026-SECRET
ADMIN_SECRET_KEY=bestuncrackableKey2029
```

5. Start local DB (optional if already running)

- With Docker:

```bash
docker run -d --name nodetrace_db -e POSTGRES_USER=nodetrace -e POSTGRES_PASSWORD=nodetrace_password -e POSTGRES_DB=nodetrace_db -p 5432:5432 postgres:15
```

6. Start FastAPI

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Local Setup (Docker)

1. Change directory to backend-py

```bash
cd NodeTrace/backend-py
```

2. Start Docker Compose

```bash
docker compose up --build
```

3. API is available at http://localhost:8000

---

## Main API Endpoints

### Admin

- `POST /auth/register`
  - body: `{ "username": "admin", "password": "..." }`

- `POST /auth/login`
  - body: `{ "username": "admin", "password": "..." }`
  - response: `{ "access_token": "..." }`

### Agent

- `POST /api/v1/register` (agent enrollment)
- `POST /api/v1/update` (telemetry update, requires Bearer token)
- `POST /api/v1/heartbeat` (heartbeat, requires Bearer token)

### Dashboard

- `GET /api/v1/devices`
- `GET /api/v1/devices/{device_id}`
- `GET /api/v1/telemetry/{device_id}`
- `GET /api/v1/status`

---

## Testing

The project includes unit tests under `tests/`.

Run:

```bash
pytest -q
```

---

## Linting

Optional:

```bash
pip install ruff black
ruff check .
black .
```