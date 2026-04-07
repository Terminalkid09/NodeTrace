# NodeTrace

A comprehensive multi-agent device monitoring platform that collects detailed telemetry data from devices across various operating systems. Features real-time monitoring, alerting, and a RESTful API for device management.

## Features

- **Multi-Agent Support**: Native agents for Windows, Linux, macOS in C#, Java, Python, C++
- **Comprehensive Telemetry**: CPU usage, RAM usage, disk space, network statistics, active connections, running processes
- **Real-Time Alerting**: Automatic alerts for high resource usage, low disk space, and network anomalies
- **Device Management**: Secure device registration, heartbeat monitoring, online/offline status tracking
- **Admin Dashboard API**: Complete RESTful API for device monitoring and alert management
- **Security**: JWT authentication, per-device rate limiting, secure enrollment with keys
- **Docker Support**: Easy deployment with Docker Compose and PostgreSQL

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Agents        │    │   Backend       │
│  (C#, Java,     │◄──►│  (FastAPI)      │
│   Python, C++)  │    │                 │
│                 │    │  ┌─────────────┐│
│ • Telemetry     │    │  │ PostgreSQL  ││
│ • Heartbeats    │    │  └─────────────┘│
│ • Auto Alerts   │    │                 │
└─────────────────┘    │ • REST API      │
                       │ • JWT Auth      │
                       │ • Rate Limiting │
                       └─────────────────┘
```

## Components

- **backend-py/**: FastAPI backend with PostgreSQL, alerting, and rate limiting
- **agents/csharp/**: .NET agent for Windows with WMI integration
- **agents/java/**: Maven-based agent for cross-platform with OSHI library
- **agents/python/**: Python agent with psutil for system monitoring
- **agents/cpp/**: C++ agent with CMake build system
- **frontend/**: (Planned) Web dashboard for visualization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- For local development: Python 3.8+, .NET SDK, Java JDK, CMake

### Backend Setup with Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/Terminalkid09/NodeTrace/
   cd NodeTrace
   ```

2. Start the backend services:
   ```bash
   cd backend-py
   docker-compose up --build
   ```

3. The API will be available at http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Running Agents

#### Python Agent (Cross-platform)
```bash
cd agents/python
pip install requests psutil
python agent.py
```

#### C# Agent (Windows)
```bash
cd agents/csharp/NodeTraceAgent
dotnet build
dotnet run
```

#### Java Agent (Cross-platform)
```bash
cd agents/java
mvn clean compile
java -cp target/classes com.nodetrace.Agent
```

#### C++ Agent (Cross-platform)
```bash
cd agents/cpp
mkdir build && cd build
cmake ..
make
./agent
```

## API Overview

### Authentication
- Admin endpoints require JWT tokens
- Agent endpoints use device-specific Bearer tokens
- Rate limiting applied per device/IP

### Key Endpoints
- `POST /register` - Register new devices
- `POST /update` - Submit telemetry data
- `POST /heartbeat` - Device heartbeat
- `GET /devices` - List all devices
- `GET /devices/{id}` - Device details with alerts
- `GET /alerts` - List all alerts
- `PUT /alerts/{id}/resolve` - Resolve alerts

### Alert Thresholds
- CPU > 90% (Critical)
- RAM > 95% (Critical)
- Disk free < 1GB (Warning) / < 512MB (Critical)
- Active connections > 100 (Warning)

## Development

### Backend Development
```bash
cd backend-py
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Testing
```bash
cd backend-py
python -m pytest tests/
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `ENROLL_KEY`: Device enrollment key
- `SKIP_DB_CREATE`: Skip database table creation (for testing)

## Security

- **Rate Limiting**: Per-device for agents, per-IP for admin
- **Authentication**: JWT for admin, device tokens for agents
- **Input Validation**: Pydantic schemas for all API inputs
- **CORS**: Configured for frontend integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

**Terminalkid09**