#include "system_info.hpp"
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <array>
#include <memory>

#ifdef _WIN32
#include <windows.h>
#include <iphlpapi.h>
#include <wmic.h>
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")
#else
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>
#endif

std::string exec(const std::string& cmd) {
    std::array<char, 256> buffer;
    std::string result;
#ifdef _WIN32
    FILE* pipe = _popen(cmd.c_str(), "r");
#else
    FILE* pipe = popen(cmd.c_str(), "r");
#endif
    if (!pipe) return "";
    while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
        result += buffer.data();
    }
#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    return result;
}

SystemInfoData SystemInfo::collect() {
    SystemInfoData info;

    // Hostname
#ifdef _WIN32
    char hostname[256];
    if (gethostname(hostname, sizeof(hostname)) == 0) {
        info.hostname = hostname;
    } else {
        info.hostname = "unknown";
    }
#else
    char hostname[256];
    if (gethostname(hostname, sizeof(hostname)) == 0) {
        info.hostname = hostname;
    } else {
        info.hostname = "unknown";
    }
#endif

    // OS info
#ifdef _WIN32
    OSVERSIONINFOEX osvi;
    ZeroMemory(&osvi, sizeof(OSVERSIONINFOEX));
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);
    GetVersionEx((LPOSVERSIONINFO)&osvi);
    info.os = "Windows";
    info.os_version = std::to_string(osvi.dwMajorVersion) + "." + std::to_string(osvi.dwMinorVersion) + "." + std::to_string(osvi.dwBuildNumber);
    
    // CPU model
    std::string cpuCmd = "wmic cpu get name";
    std::string cpuOutput = exec(cpuCmd);
    if (!cpuOutput.empty()) {
        size_t pos = cpuOutput.find('\n');
        if (pos != std::string::npos) {
            info.cpu_model = cpuOutput.substr(pos + 1);
            info.cpu_model.erase(info.cpu_model.find_last_not_of(" \n\r\t") + 1);
        }
    }
    if (info.cpu_model.empty()) {
        info.cpu_model = "unknown";
    }
#else
    struct utsname unameData;
    uname(&unameData);
    info.os = unameData.sysname;
    info.os_version = unameData.release;
    
    // CPU model from /proc/cpuinfo
    std::ifstream cpuinfo("/proc/cpuinfo");
    if (cpuinfo.is_open()) {
        std::string line;
        while (std::getline(cpuinfo, line)) {
            if (line.find("model name") != std::string::npos) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    info.cpu_model = line.substr(pos + 2); // +2 to skip ": "
                    break;
                }
            }
        }
        cpuinfo.close();
    }
    if (info.cpu_model.empty()) {
        info.cpu_model = "unknown";
    }
#endif

    // RAM total
#ifdef _WIN32
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    if (GlobalMemoryStatusEx(&memInfo)) {
        info.ram_total = memInfo.ullTotalPhys / (1024 * 1024); // MB
    } else {
        info.ram_total = 0;
    }
#else
    // For Linux, use sysinfo
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        info.ram_total = si.totalram / (1024 * 1024); // MB
    } else {
        info.ram_total = 0;
    }
#endif

    return info;
}