#include "system_info.hpp"
#include <iostream>
#include <string>
#ifdef _WIN32
#include <windows.h>
#include <iphlpapi.h>
#pragma comment(lib, "iphlpapi.lib")
#else
#include <unistd.h>
#include <sys/utsname.h>
#endif

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
    OSVERSIONINFO osvi;
    ZeroMemory(&osvi, sizeof(OSVERSIONINFO));
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
    GetVersionEx(&osvi);
    info.os = "Windows";
    info.os_version = std::to_string(osvi.dwMajorVersion) + "." + std::to_string(osvi.dwMinorVersion) + "." + std::to_string(osvi.dwBuildNumber);
#else
    struct utsname unameData;
    uname(&unameData);
    info.os = unameData.sysname;
    info.os_version = unameData.release;
#endif

    // CPU model - placeholder
    info.cpu_model = "unknown";

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
    // For Linux, use sysinfo or /proc/meminfo
    info.ram_total = 0; // placeholder
#endif

    return info;
}