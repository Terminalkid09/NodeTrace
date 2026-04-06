#pragma once
#include <string>

struct SystemInfoData {
    std::string hostname;
    std::string os;
    std::string os_version;
    std::string cpu_model;
    long ram_total;
};

class SystemInfo {
public:
    static SystemInfoData collect();
};