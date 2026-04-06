#include "config.hpp"
#include <fstream>
#include <nlohmann/json.hpp>

Config Config::load(const std::string& path) {
    std::ifstream file(path);
    nlohmann::json j;
    file >> j;

    Config cfg;
    cfg.device_name = j["device_name"];
    cfg.register_url = j["register_url"];
    cfg.update_url = j["update_url"];
    cfg.heartbeat_url = j["heartbeat_url"];
    cfg.heartbeat_interval = j["heartbeat_interval"];
    cfg.retry_max_attempts = j["retry_max_attempts"];
    cfg.retry_base_delay = j["retry_base_delay"];
    cfg.enroll_key = j["enroll_key"];

    return cfg;
}