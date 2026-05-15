#include "config.hpp"
#include <fstream>
#include <nlohmann/json.hpp>

#include <filesystem>
#include <iostream>

Config Config::load(const std::string& path) {
    std::string config_path = path;
    if (!std::filesystem::exists(config_path)) {
        config_path = "agents/cpp/config.json";
    }
    
    if (!std::filesystem::exists(config_path)) {
        config_path = "../config.json"; // relative to build dir
    }

    std::ifstream file(config_path);
    if (!file.is_open()) {
        std::cerr << "ERROR: Could not open config file: " << config_path << std::endl;
        exit(1);
    }
    
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