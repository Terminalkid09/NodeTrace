#pragma once
#include "config.hpp"
#include "http_client.hpp"

class HeartbeatService {
public:
    HeartbeatService(const Config& cfg);

    void start();

private:
    Config config;
    HttpClient client;
};