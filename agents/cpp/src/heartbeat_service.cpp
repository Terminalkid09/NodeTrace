#include "heartbeat_service.hpp"
#include "logger.hpp"

HeartbeatService::HeartbeatService(const Config& cfg)
    : config(cfg) {}

void HeartbeatService::start() {
    Logger::info("Heartbeat service started");
}