#pragma once
#include <string>
#include <vector>

struct TelemetryData {
    double cpu_usage;
    double ram_usage;
    std::string ip_local;
    std::string ip_public;
    std::string geo_country;
    std::string geo_city;
    std::vector<std::string> processes;
    long disk_free;
    long disk_total;
    long network_sent;
    long network_received;
    int active_connections;
};

struct NetworkData {
    std::string mac_address;
    std::string ip_local;
    std::string ip_public;
};

class TelemetryService {
public:
    static TelemetryData collect();
    static NetworkData collectNetworkInfo();

private:
    static std::string getPublicIp();
    static std::string getLocalIp();
    static std::string getMacAddress();
    static double getCpuUsage();
    static double getRamUsage();
    static std::pair<long, long> getDiskInfo();
    static std::pair<long, long> getNetworkStats();
    static std::vector<std::string> getTopProcesses();
    static int getActiveConnections();
};
