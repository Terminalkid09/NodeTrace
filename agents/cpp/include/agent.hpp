#pragma once
#include "config.hpp"
#include "heartbeat_service.hpp"
#include "system_info.hpp"
#include "http_client.hpp"

class Agent {
public:
    Agent(const Config& cfg);
    void start();

private:
    Config config;
    HeartbeatService heartbeat;
    SystemInfoData system_info;
    HttpClient http;

    std::string register_device();
    void send_telemetry(const std::string& device_id);
    void send_heartbeat(const std::string& device_id);
};