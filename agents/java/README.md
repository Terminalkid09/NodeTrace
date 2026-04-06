# NodeTrace Java Agent

A cross-platform Java agent for the NodeTrace monitoring system. Uses the OSHI (Operating System and Hardware Information) library to collect comprehensive system telemetry on Windows, Linux, and macOS.

## Features

- **Cross-Platform**: Full support for Windows, Linux, macOS using OSHI
- **Comprehensive Telemetry**: CPU usage, RAM usage, disk space, network I/O, active connections, running processes
- **Hardware Detection**: Detailed CPU, memory, and storage information
- **Automatic Registration**: Secure device enrollment with shared secret
- **Reliable Communication**: Configurable retry logic with exponential backoff
- **Maven-Based**: Standard Java build and dependency management
- **Configurable**: JSON-based configuration for all settings

## Requirements

- Java 11 or later
- Maven 3.6+
- OSHI library (automatically included via Maven)

## Installation

### From Source
```bash
git clone https://github.com/yourusername/NodeTrace.git
cd NodeTrace/agents/java
mvn clean install
```

### Build Only
```bash
mvn clean compile
```

### Run
```bash
mvn exec:java -Dexec.mainClass="com.nodetrace.Agent"
```

## Configuration

Create a `config.json` file in the project root:

```json
{
  "device_name": "MyLinuxServer",
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
mvn exec:java -Dexec.mainClass="com.nodetrace.Agent"
```

### Production
```bash
mvn clean package
java -jar target/nodetrace-java-agent-1.0.jar
```

### Docker Usage
```bash
docker build -t nodetrace-java-agent .
docker run -v $(pwd)/config.json:/app/config.json nodetrace-java-agent
```

## Telemetry Data

The agent collects the following metrics using OSHI:

- **CPU Usage**: Real-time CPU utilization across all cores
- **RAM Usage**: Current memory utilization percentage
- **Disk Information**: Free and total disk space across all partitions
- **Network Statistics**: Bytes sent/received across all interfaces
- **Active Connections**: Number of active network connections
- **Running Processes**: List of top CPU-consuming processes
- **System Information**: OS details, hostname, IP addresses, geolocation

## Architecture

```
Agent.java (Main)
├── Registration: Device enrollment with backend
├── Telemetry Collection (TelemetryService.java)
│   ├── OSHI system information queries
│   ├── Hardware abstraction layer
│   ├── Process enumeration
│   └── Network monitoring
├── Communication (AgentService.java)
│   ├── HTTP client with retry logic
│   ├── Exponential backoff
│   └── Error handling
└── Heartbeat: Periodic status updates
```

## Dependencies

- **oshi-core**: Hardware and system information library
- **oshi-json**: JSON serialization support
- **gson**: JSON parsing and serialization
- **slf4j-api**: Logging facade
- **logback-classic**: Logging implementation

## Security

- Device registration requires valid enrollment key
- All communication uses Bearer token authentication
- Rate limiting enforced by backend
- No sensitive data transmitted

## Troubleshooting

### OSHI Access Issues
- On Linux, may need elevated permissions for some hardware info
- On macOS, ensure System Integrity Protection allows access
- On Windows, WMI service should be running

### Memory Issues
- OSHI can be memory-intensive on systems with many processes
- Adjust telemetry interval if memory usage is too high

### Connection Issues
- Verify backend URL is correct and accessible
- Check enrollment key matches backend configuration
- Ensure firewall allows outbound HTTP connections

## Development

### Running Tests
```bash
mvn test
```

### Code Structure
- `Agent.java`: Main application class
- `TelemetryService.java`: System monitoring and data collection
- `AgentService.java`: HTTP communication and API integration
- `TelemetryData.java`: Data models for telemetry payload
- `config.json`: Configuration file

### Adding New Metrics
1. Extend `TelemetryData.java` with new fields
2. Update `TelemetryService.java` to collect data using OSHI
3. Update backend models/schemas to handle new fields

## Contributing

1. Follow Java coding standards and naming conventions
2. Add unit tests for new features
3. Update documentation
4. Submit pull request

## License

MIT License

- `device_name`: Unique name for this device
- `register_url`: Backend registration endpoint
- `update_url`: Telemetry update endpoint
- `heartbeat_url`: Heartbeat endpoint
- `enroll_key`: Secret key for enrollment
- `telemetry_interval_seconds`: Telemetry send interval
- `heartbeat_interval_seconds`: Heartbeat send interval
- `retry_max_attempts`: Max retry attempts
- `retry_base_delay`: Base delay for retries

## Data Collected

- CPU usage percentage
- RAM usage (used/total)
- OS information
- Uptime
- Hostname
- MAC address
- Network information
- Process list (optional)

## Architecture

- `Agent.java`: Main agent class
- `services/TelemetryService.java`: System monitoring
- `services/NetworkService.java`: Network utilities
- `services/TokenService.java`: Token management
- `services/RetryPolicy.java`: Retry logic
- `utils/Logger.java`: Logging utilities

## Dependencies

- OSHI: Hardware monitoring
- Gson: JSON processing
- OkHttp: HTTP client

## Troubleshooting

- Ensure Java and Maven are installed
- Check backend connectivity
- Verify `enroll_key` configuration
- Review logs for errors</content>
<parameter name="filePath">c:\Users\ilysm\Desktop\GitHub\NodeTrace\agents\java\README.md
