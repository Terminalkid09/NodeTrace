# NodeTrace C++ Agent placeholder

A high-performance C++ agent for the NodeTrace monitoring system. Designed for resource-constrained environments with minimal dependencies and efficient system monitoring.

## Features

- **High Performance**: Low CPU and memory footprint
- **Cross-Platform**: Windows, Linux, macOS support
- **Comprehensive Telemetry**: CPU usage, RAM usage, disk space, network I/O, active connections, running processes
- **Automatic Registration**: Secure device enrollment with shared secret
- **Reliable Communication**: Configurable retry logic with exponential backoff
- **CMake Build System**: Professional build configuration
- **Minimal Dependencies**: Only libcurl and nlohmann/json required

## Requirements

- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.10+
- libcurl development libraries
- nlohmann/json library

## Installation

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install build-essential cmake libcurl4-openssl-dev nlohmann-json3-dev
```

### macOS
```bash
brew install cmake curl nlohmann-json
```

### Windows (vcpkg)
```bash
vcpkg install curl nlohmann-json
```

### From Source
```bash
git clone https://github.com/Terminalkid09/NodeTrace/tree/main/agents/cpp
cd NodeTrace/agents/cpp
mkdir build && cd build
cmake ..
make
```

## Configuration

Create a `config.json` file in the executable directory:

```json
{
  "device_name": "MyEmbeddedDevice",
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

### Basic Operation
```bash
./nodetrace_agent
```

### Docker Usage
```bash
docker build -t nodetrace-cpp-agent .
docker run -v $(pwd)/config.json:/app/config.json nodetrace-cpp-agent
```

## Telemetry Data

The agent collects the following metrics:

- **CPU Usage**: Current CPU utilization percentage
- **RAM Usage**: Current memory utilization percentage
- **Disk Information**: Free and total disk space (MB)
- **Network Statistics**: Bytes sent/received since boot
- **Active Connections**: Number of active network connections
- **Running Processes**: List of top CPU-consuming processes
- **System Information**: OS, hostname, IP addresses, geolocation

## Architecture

```
main.cpp (Main)
├── Registration: Device enrollment with backend
├── Telemetry Collection (telemetry.cpp)
│   ├── Platform-specific system calls
│   ├── CPU/RAM monitoring via /proc or Windows APIs
│   ├── Disk usage statistics
│   ├── Network I/O counters
│   └── Process enumeration
├── Communication (network.cpp)
│   ├── libcurl HTTP client
│   ├── Retry logic with exponential backoff
│   └── Error handling
└── Heartbeat: Periodic status updates
```

## Build System

### Debug Build
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make
```

### Release Build
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

### Cross-Compilation
```bash
cmake -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake ..
```

## Dependencies

- **libcurl**: HTTP client library for communication
- **nlohmann/json**: JSON parsing and serialization
- **CMake**: Build system configuration

## Security

- Device registration requires valid enrollment key
- All communication uses Bearer token authentication
- Rate limiting enforced by backend
- No sensitive data transmitted

## Troubleshooting

### Build Issues
- Ensure all dependencies are installed
- Check CMake version is 3.10 or higher
- Verify compiler supports C++17

### Runtime Issues
- Check config.json is in the working directory
- Verify backend URLs are accessible
- Ensure libcurl shared libraries are available

### Performance Issues
- Adjust telemetry intervals for resource-constrained systems
- Monitor memory usage on embedded devices

## Development

### Code Structure
- `main.cpp`: Application entry point and main loop
- `telemetry.cpp/.h`: System monitoring functions
- `network.cpp/.h`: HTTP communication utilities
- `config.json`: Configuration file

### Platform-Specific Code
- Windows: Uses Windows API and WMI
- Linux: Uses /proc filesystem and syscalls
- macOS: Uses sysctl and IOKit

### Adding New Metrics
1. Extend telemetry data structures
2. Implement platform-specific collection in telemetry.cpp
3. Update JSON payload construction
4. Update backend models/schemas

## Contributing

1. Follow C++ Core Guidelines
2. Add unit tests for new features
3. Update documentation
4. Submit pull request

## License

MIT License
   ```bash
   mkdir build
   cd build
   cmake ..
   make
   ```

5. Run:
   ```bash
   ./NodeTraceAgent
   ```

## Configuration

- `device_name`: Unique device name
- `register_url`: Backend registration endpoint
- `update_url`: Telemetry update endpoint
- `heartbeat_url`: Heartbeat endpoint
- `enroll_key`: Enrollment secret key
- `telemetry_interval_seconds`: Telemetry send interval
- `heartbeat_interval_seconds`: Heartbeat interval
- `retry_max_attempts`: Max retry attempts
- `retry_base_delay`: Base retry delay

## Data Collected

- CPU usage (placeholder)
- RAM total (MB)
- OS information
- OS version
- CPU model (placeholder)
- Hostname
- MAC address (placeholder)
- Network information (placeholder)

## Architecture

- `src/agent.cpp`: Main agent loop and logic
- `src/system_info.cpp`: System information collection
- `src/http_client.cpp`: HTTP communication
- `src/logger.cpp`: Logging utilities
- `include/`: Header files
- `CMakeLists.txt`: Build configuration

## Platform Notes

### Windows
- Uses Windows API for system information
- Requires Windows SDK for compilation

### Linux
- Uses uname and sysinfo system calls
- May require additional libraries for full functionality

### macOS
- Similar to Linux, with potential modifications needed
