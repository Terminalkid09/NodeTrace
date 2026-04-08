#include "agent.hpp"
#include "logger.hpp"
#include "http_client.hpp"
#include "telemetry_data.hpp"
#include <nlohmann/json.hpp>
#include <thread>
#include <chrono>

Agent::Agent(const Config& cfg)
    : config(cfg), heartbeat(cfg) {}

void Agent::start() {
    Logger::info("Collecting system info...");
    system_info = SystemInfo::collect();

    Logger::info("Hostname: " + system_info.hostname);
    Logger::info("OS: " + system_info.os);

    // Register
    std::string device_id = register_device();
    if (device_id.empty()) {
        Logger::error("Registration failed");
        return;
    }

    Logger::info("Device registered: " + device_id);

    // Start loop
    while (true) {
        send_telemetry(device_id);
        send_heartbeat(device_id);
        std::this_thread::sleep_for(std::chrono::seconds(config.heartbeat_interval));
    }
}

std::string Agent::register_device() {
    NetworkData net = TelemetryService::collectNetworkInfo();
    
    nlohmann::json payload = {
        {"hostname", config.device_name},
        {"os", system_info.os},        
        {"os_version", system_info.os_version},
        {"cpu_model", system_info.cpu_model},
        {"total_ram", system_info.ram_total},
        {"mac_address", net.mac_address},
        {"enroll_key", config.enroll_key}
    };

    HttpClient http;
    std::string response = http.post(config.register_url, payload.dump());

    if (response == "error") {
        return "";
    }

    auto json = nlohmann::json::parse(response);
    return json["device_id"];
}

void Agent::send_telemetry(const std::string& device_id) {
    // Collect telemetry data
    TelemetryData telemetry = TelemetryService::collect();

    nlohmann::json processes = nlohmann::json::array();
    for (const auto& process : telemetry.processes) {
        processes.push_back(process);
    }

    nlohmann::json payload = {
        {"device_id", device_id},
        {"cpu_usage", telemetry.cpu_usage},
        {"ram_usage", telemetry.ram_usage},
        {"ip_local", telemetry.ip_local},
        {"ip_public", telemetry.ip_public},
        {"geo_country", nullptr},
        {"geo_city", nullptr},
        {"processes", processes},
        {"disk_free", telemetry.disk_free},
        {"disk_total", telemetry.disk_total},
        {"network_sent", telemetry.network_sent},
        {"network_received", telemetry.network_received},
        {"active_connections", telemetry.active_connections}
    };

    HttpClient http;
    std::string response = http.post(config.update_url, payload.dump());
    (void)response;
    Logger::info("Telemetry sent");
}

void Agent::send_heartbeat(const std::string& device_id) {
    nlohmann::json payload = {
        {"device_id", device_id}
    };

    HttpClient http;
    std::string response = http.post(config.heartbeat_url, payload.dump());
    Logger::info("Heartbeat sent");
}