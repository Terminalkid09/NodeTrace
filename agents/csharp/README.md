# NodeTrace C# Agent

A cross-platform .NET agent for the NodeTrace monitoring system. Collects comprehensive Windows system telemetry using WMI (Windows Management Instrumentation) and Performance Counters.

## Features

- **Windows-Optimized**: Uses WMI and Performance Counters for accurate metrics
- **Comprehensive Telemetry**: CPU usage, RAM usage, disk space, network I/O, active connections, running processes
- **Automatic Registration**: Secure device enrollment with shared secret
- **Reliable Communication**: Configurable retry logic with exponential backoff
- **Cross-Platform**: .NET 6+ supports Windows, Linux, macOS
- **Configurable**: JSON-based configuration for all settings

## Requirements

- .NET 6.0 or later
- Windows (full WMI support), Linux/macOS (.NET runtime required)

## Installation

### From Source
```bash
git clone https://github.com/Terminalkid09/NodeTrace/tree/main/agents/csharp
cd NodeTrace/agents/csharp/NodeTraceAgent
dotnet restore
```

### Build
```bash
dotnet build --configuration Release
```

### Run
```bash
dotnet run --project NodeTraceAgent.csproj
```

## Configuration

Create a `config.json` file in the project directory:

```json
{
  "device_name": "MyWindowsWorkstation",
  "register_url": "http://localhost:8000/api/v1/register",
  "update_url": "http://localhost:8000/api/v1/update",
  "heartbeat_url": "http://localhost:8000/api/v1/heartbeat",
  "enroll_key": "your-enrollment-secret-key",
  "telemetry_interval_seconds": 30,
  "heartbeat_interval_seconds": 60,
  "retry_max_attempts": 5,
  "retry_base_delay": 1.0
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `device_name` | Human-readable device identifier | Required |
| `register_url` | Backend registration endpoint | Required |
| `update_url` | Telemetry submission endpoint | Required |
| `heartbeat_url` | Heartbeat endpoint | Required |
| `enroll_key` | Device enrollment secret | Required |
| `telemetry_interval_seconds` | How often to send telemetry | 30 |
| `heartbeat_interval_seconds` | How often to send heartbeat | 60 |
| `retry_max_attempts` | Max retry attempts for failed requests | 5 |
| `retry_base_delay` | Base delay for exponential backoff (seconds) | 1.0 |

## Usage

### Development
```bash
dotnet run
```

### Production
```bash
dotnet publish --configuration Release --runtime win-x64 --self-contained
cd bin/Release/net6.0/win-x64/publish
./NodeTraceAgent.exe
```

### Docker Usage
```bash
docker build -t nodetrace-csharp-agent .
docker run -v $(pwd)/config.json:/app/config.json nodetrace-csharp-agent
```

## Telemetry Data

The agent collects the following metrics using Windows-specific APIs:

- **CPU Usage**: Real-time CPU utilization via Performance Counters
- **RAM Usage**: Current memory utilization percentage
- **Disk Information**: Free and total disk space using WMI
- **Network Statistics**: Bytes sent/received via Performance Counters
- **Active Connections**: Number of active TCP connections
- **Running Processes**: List of top CPU-consuming processes via WMI
- **System Information**: Windows version, hostname, IP addresses, geolocation

## Architecture

```
Program.cs (Main)
├── Registration: Device enrollment with backend
├── Telemetry Collection (TelemetryService.cs)
│   ├── WMI queries for system information
│   ├── Performance Counter monitoring
│   ├── Process enumeration
│   └── Network statistics
├── Communication (AgentService.cs)
│   ├── HTTP client with retry logic
│   ├── Exponential backoff
│   └── Error handling
└── Heartbeat: Periodic status updates
```

## Security

- Device registration requires valid enrollment key
- All communication uses Bearer token authentication
- Rate limiting enforced by backend
- No sensitive data transmitted

## Troubleshooting

### WMI Access Issues
- Ensure agent runs with appropriate permissions
- On Windows, may need to run as Administrator for full WMI access
- Check Windows Management Instrumentation service is running

### Performance Counter Issues
- Some counters may require elevated privileges
- Ensure no other monitoring tools are conflicting

### Connection Issues
- Verify backend URL is correct and accessible
- Check enrollment key matches backend configuration
- Ensure firewall allows outbound HTTP connections

## Development

### Running Tests
```bash
dotnet test
```

### Code Structure
- `Program.cs`: Main application entry point
- `TelemetryService.cs`: System monitoring and data collection
- `AgentService.cs`: HTTP communication and API integration
- `TelemetryData.cs`: Data models for telemetry payload
- `config.json`: Configuration file

### Adding New Metrics
1. Extend `TelemetryData.cs` with new properties
2. Update `TelemetryService.cs` to collect the data
3. Update backend models/schemas to handle new fields

## Contributing

1. Follow C# coding standards and naming conventions
2. Add unit tests for new features
3. Update documentation
4. Submit pull request

## License

MIT License
- `register_url`: Backend registration endpoint
- `update_url`: Telemetry update endpoint
- `heartbeat_url`: Heartbeat endpoint
- `enroll_key`: Secret key for enrollment
- `telemetry_interval_seconds`: How often to send telemetry
- `heartbeat_interval_seconds`: How often to send heartbeat
- `retry_max_attempts`: Max retry attempts for failed requests
- `retry_base_delay`: Base delay for exponential backoff

## Data Collected

- CPU usage percentage
- Available RAM in MB
- OS version string
- Uptime in seconds
- Hostname
- MAC address
- Public and local IP addresses
- Geographic location (if available)
- Running processes (optional)

## Architecture

- `Program.cs`: Entry point
- `Services/AgentService.cs`: Main agent logic
- `Services/TelemetryService.cs`: System monitoring
- `Services/NetworkService.cs`: Network information
- `Services/TokenService.cs`: Token persistence
- `Models/`: Data models
- `Utils/`: Utilities and helpers

