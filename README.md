# NodeTrace

A comprehensive multi-agent device monitoring platform that collects detailed telemetry data from devices across various operating systems. Features real-time monitoring, alerting, and a RESTful API for device management.

## 🚀 New Features

- **🧠 Real-Time Statistical Anomaly Detection**: Uses a Z-Score engine to identify unusual resource spikes (CPU/RAM) based on historical data windows, going beyond simple static thresholds.
- **🛠️ Unified Interactive Installer**: A single script to install, configure, and uninstall all 4 types of agents (Python, C++, C#, Java).
- **📊 Dynamic Chart Highlighting**: Visual cues in the dashboard that glow and highlight data points flagged as anomalies.

## Features

- **Multi-Agent Support**: Native agents for Windows, Linux, macOS in C#, Java, Python, C++
- **Comprehensive Telemetry**: CPU usage, RAM usage, disk space, network statistics, active connections, running processes
- **Real-Time Alerting**: Automatic alerts for high resource usage, low disk space, and **Statistical Anomalies**
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
│ • Telemetry     │    │  │ Anomaly Eng ││
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
- **frontend/**: Web dashboard for device monitoring and visualization

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
   - Health Check: http://localhost:8000/api/v1/health

### Running Agents
Use the **Unified Installer** for a guided setup:
```bash
.\install_agent.bat
```

## API Overview

### Authentication
- Admin endpoints require JWT tokens
- Agent endpoints use device-specific Bearer tokens
- Rate limiting applied per device/IP

### Key Endpoints
- `POST /api/v1/register` - Register new devices
- `POST /api/v1/update` - Submit telemetry data with Anomaly Detection
- `POST /api/v1/heartbeat` - Device heartbeat
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/alerts` - List all alerts (including Statistical Anomalies)

## Security

- **Rate Limiting**: Per-device for agents, per-IP for admin
- **Authentication**: JWT for admin, device tokens for agents
- **Input Validation**: Pydantic schemas for all API inputs
- **Anomaly Detection**: Statistical Z-Score analysis for behavioral security

## Author
**Terminalkid09**
