#include "config.hpp"
#include "agent.hpp"
#include "logger.hpp"

int main() {
    Logger::info("Loading config...");
    Config cfg = Config::load("config.json");

    Logger::info("Starting agent...");
    Agent agent(cfg);
    agent.start();

    return 0;
}