#pragma once
#include <string>

struct Config {
    std::string device_name;
    std::string register_url;
    std::string update_url;
    std::string heartbeat_url;
    int heartbeat_interval;
    int retry_max_attempts;
    int retry_base_delay;
    std::string enroll_key;

    static Config load(const std::string& path);
};