#include "telemetry_data.hpp"
#include "logger.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <array>
#include <cstring>
#include <algorithm>

#ifdef _WIN32
#include <windows.h>
#include <iphlpapi.h>
#include <psapi.h>
#include <winsock2.h>
#include <wininet.h>
#include <tlhelp32.h>
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "wsock32.lib")
#pragma comment(lib, "winsock2.lib")
#pragma comment(lib, "wininet.lib")
#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "kernel32.lib")
#else
#include <unistd.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
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
    // Remove trailing whitespace
    result.erase(result.find_last_not_of(" \n\r\t") + 1);
    return result;
}

TelemetryData TelemetryService::collect() {
    TelemetryData data;
    data.cpu_usage = getCpuUsage();
    data.ram_usage = getRamUsage();
    
    NetworkData net = collectNetworkInfo();
    data.ip_local = net.ip_local;
    data.ip_public = net.ip_public;
    
    data.geo_country = "";
    data.geo_city = "";
    data.processes = getTopProcesses();
    
    auto diskInfo = getDiskInfo();
    data.disk_free = diskInfo.first;
    data.disk_total = diskInfo.second;
    
    auto netStats = getNetworkStats();
    data.network_sent = netStats.first;
    data.network_received = netStats.second;
    
    data.active_connections = getActiveConnections();
    
    return data;
}

NetworkData TelemetryService::collectNetworkInfo() {
    NetworkData data;
    data.mac_address = getMacAddress();
    data.ip_local = getLocalIp();
    data.ip_public = getPublicIp();
    return data;
}

std::string TelemetryService::getLocalIp() {
#ifdef _WIN32
    char hostname[256];
    if (gethostname(hostname, sizeof(hostname)) != 0) {
        return "127.0.0.1";
    }
    
    struct hostent *he = gethostbyname(hostname);
    if (he == nullptr) {
        return "127.0.0.1";
    }
    
    return inet_ntoa(*(struct in_addr *)*he->h_addr_list);
#else
    struct ifaddrs *ifaddr, *ifa;
    std::string result = "127.0.0.1";
    
    if (getifaddrs(&ifaddr) == -1) {
        return result;
    }
    
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) continue;
        
        if (ifa->ifa_addr->sa_family == AF_INET) {
            struct sockaddr_in *addr = (struct sockaddr_in *)ifa->ifa_addr;
            std::string ip = inet_ntoa(addr->sin_addr);
            
            if (ip != "127.0.0.1" && ip.find("127.") != 0) {
                result = ip;
                break;
            }
        }
    }
    
    freeifaddrs(ifaddr);
    return result;
#endif
}

std::string TelemetryService::getPublicIp() {
    try {
        std::string result = exec("curl -s https://api.ipify.org");
        if (!result.empty()) {
            return result;
        }
    } catch (...) {
    }
    return "unknown";
}

std::string TelemetryService::getMacAddress() {
#ifdef _WIN32
    PIP_ADAPTER_INFO pAdapterInfo;
    PIP_ADAPTER_INFO pAdapter = NULL;
    DWORD dwRetVal = 0;
    ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);
    
    pAdapterInfo = (IP_ADAPTER_INFO *)malloc(sizeof(IP_ADAPTER_INFO));
    
    if (GetAdaptersInfo(pAdapterInfo, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW) {
        free(pAdapterInfo);
        pAdapterInfo = (IP_ADAPTER_INFO *)malloc(ulOutBufLen);
    }
    
    std::string mac = "unknown";
    
    if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == NO_ERROR) {
        pAdapter = pAdapterInfo;
        while (pAdapter) {
            if (pAdapter->Type == MIB_IF_TYPE_ETHERNET && pAdapter->AddressLength == 6) {
                char macStr[18];
                sprintf_s(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X",
                    pAdapter->Address[0], pAdapter->Address[1], pAdapter->Address[2],
                    pAdapter->Address[3], pAdapter->Address[4], pAdapter->Address[5]);
                mac = macStr;
                break;
            }
            pAdapter = pAdapter->Next;
        }
    }
    
    if (pAdapterInfo) free(pAdapterInfo);
    return mac;
#else
    struct ifaddrs *ifaddr, *ifa;
    std::string mac = "unknown";
    
    if (getifaddrs(&ifaddr) == -1) {
        return mac;
    }
    
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) continue;
        
        if (ifa->ifa_addr->sa_family == AF_LINK) {
            struct sockaddr_dl *dl = (struct sockaddr_dl *)ifa->ifa_addr;
            if (dl->sdl_alen == 6) {
                unsigned char *b = (unsigned char *)LLADDR(dl);
                char macStr[18];
                sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X",
                    b[0], b[1], b[2], b[3], b[4], b[5]);
                mac = macStr;
                break;
            }
        }
    }
    
    freeifaddrs(ifaddr);
    return mac;
#endif
}

double TelemetryService::getCpuUsage() {
#ifdef _WIN32
    FILETIME idleTime, kernelTime, userTime;
    if (GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        ULARGE_INTEGER idle, kernel, user;
        idle.LowPart = idleTime.dwLowDateTime;
        idle.HighPart = idleTime.dwHighDateTime;
        kernel.LowPart = kernelTime.dwLowDateTime;
        kernel.HighPart = kernelTime.dwHighDateTime;
        user.LowPart = userTime.dwLowDateTime;
        user.HighPart = userTime.dwHighDateTime;
        
        ULONGLONG total = kernel.QuadPart + user.QuadPart;
        if (total > 0) {
            double usage = ((double)(total - idle.QuadPart) / (double)total) * 100.0;
            return std::min(usage, 100.0);
        }
    }
    return 0.0;
#else
    std::ifstream stat("/proc/stat");
    if (!stat.is_open()) return 0.0;
    
    std::string line;
    std::getline(stat, line);
    stat.close();
    
    if (line.find("cpu") != 0) return 0.0;
    
    long user, nice, system, idle;
    if (sscanf(line.c_str(), "cpu %ld %ld %ld %ld", &user, &nice, &system, &idle) != 4) {
        return 0.0;
    }
    
    long total = user + nice + system + idle;
    if (total > 0) {
        return (double)(total - idle) / (double)total * 100.0;
    }
    return 0.0;
#endif
}

double TelemetryService::getRamUsage() {
#ifdef _WIN32
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    
    if (GlobalMemoryStatusEx(&memInfo)) {
        ULONGLONG totalPhys = memInfo.ullTotalPhys;
        ULONGLONG availPhys = memInfo.ullAvailPhys;
        if (totalPhys > 0) {
            return ((double)(totalPhys - availPhys) / (double)totalPhys) * 100.0;
        }
    }
    return 0.0;
#else
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        if (si.totalram > 0) {
            return ((double)(si.totalram - si.freeram) / (double)si.totalram) * 100.0;
        }
    }
    return 0.0;
#endif
}

std::pair<long, long> TelemetryService::getDiskInfo() {
#ifdef _WIN32
    ULARGE_INTEGER freeBytesAvailable, totalNumberOfBytes;
    
    // Convert to wide char for Windows API
    const char* pathStr = "C:\\";
    int wchars_num = MultiByteToWideChar(CP_UTF8, 0, pathStr, -1, NULL, 0);
    wchar_t* wstr = new wchar_t[wchars_num];
    MultiByteToWideChar(CP_UTF8, 0, pathStr, -1, wstr, wchars_num);
    
    BOOL result = GetDiskFreeSpaceEx(wstr, &freeBytesAvailable, &totalNumberOfBytes, NULL);
    delete[] wstr;
    
    if (result) {
        long free_mb = freeBytesAvailable.QuadPart / (1024 * 1024);
        long total_mb = totalNumberOfBytes.QuadPart / (1024 * 1024);
        return std::make_pair(free_mb, total_mb);
    }
    return std::make_pair(0, 0);
#else
    std::ifstream meminfo("/proc/meminfo");
    if (!meminfo.is_open()) return std::make_pair(0, 0);
    
    std::string line;
    long memTotal = 0, memAvail = 0;
    
    while (std::getline(meminfo, line)) {
        if (line.find("MemTotal:") == 0) {
            sscanf(line.c_str(), "MemTotal: %ld", &memTotal);
        }
        if (line.find("MemAvailable:") == 0) {
            sscanf(line.c_str(), "MemAvailable: %ld", &memAvail);
        }
    }
    meminfo.close();
    
    return std::make_pair(memAvail / 1024, memTotal / 1024); // Convert to MB
#endif
}

std::pair<long, long> TelemetryService::getNetworkStats() {
#ifdef _WIN32
    MIB_IFROW ifRow;
    std::vector<MIB_IFROW> ifRowList;
    
    DWORD dwSize = 0;
    if (GetIfTable(NULL, &dwSize, FALSE) == ERROR_INSUFFICIENT_BUFFER) {
        PMIB_IFTABLE pIfTable = (PMIB_IFTABLE)malloc(dwSize);
        if (GetIfTable(pIfTable, &dwSize, FALSE) == NO_ERROR) {
            long totalSent = 0, totalRecv = 0;
            for (DWORD i = 0; i < pIfTable->dwNumEntries; i++) {
                totalSent += pIfTable->table[i].dwOutOctets;
                totalRecv += pIfTable->table[i].dwInOctets;
            }
            free(pIfTable);
            return std::make_pair(totalSent, totalRecv);
        }
        free(pIfTable);
    }
    return std::make_pair(0, 0);
#else
    std::ifstream dev("/proc/net/dev");
    if (!dev.is_open()) return std::make_pair(0, 0);
    
    std::string line;
    long totalSent = 0, totalRecv = 0;
    
    while (std::getline(dev, line)) {
        if (line.find("lo:") != std::string::npos) continue;
        if (line.find(":") != std::string::npos) {
            long recv, sent;
            if (sscanf(line.c_str(), "%*s %ld %*d %*d %*d %*d %*d %*d %*d %ld", &recv, &sent) == 2) {
                totalRecv += recv;
                totalSent += sent;
            }
        }
    }
    dev.close();
    
    return std::make_pair(totalSent, totalRecv);
#endif
}

std::vector<std::string> TelemetryService::getTopProcesses() {
    std::vector<std::string> processes;
    
#ifdef _WIN32
    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE) {
        return processes;
    }
    
    PROCESSENTRY32W pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32W);
    
    if (Process32FirstW(hProcessSnap, &pe32)) {
        do {
            if (processes.size() < 5) {
                // Convert wide char to string
                char procStr[256] = {0};
                size_t converted = wcstombs(procStr, pe32.szExeFile, sizeof(procStr) - 1);
                if (converted == (size_t)-1 || converted == 0) {
                    strncpy(procStr, "Unknown", sizeof(procStr) - 1);
                }
                
                char fullStr[286] = {0};
                snprintf(fullStr, sizeof(fullStr), "%s (%ld)", procStr, pe32.th32ProcessID);
                processes.push_back(fullStr);
            }
        } while (Process32NextW(hProcessSnap, &pe32) && processes.size() < 5);
    }
    
    CloseHandle(hProcessSnap);
#else
    std::string result = exec("ps aux 2>/dev/null | sort -k3 -rn | head -5 | awk '{print $11 \" (\" $2 \")\"}'");
    if (!result.empty()) {
        std::stringstream ss(result);
        std::string line;
        while (std::getline(ss, line) && processes.size() < 5) {
            if (!line.empty()) {
                processes.push_back(line);
            }
        }
    }
#endif
    
    return processes;
}

int TelemetryService::getActiveConnections() {
#ifdef _WIN32
    std::string result = exec("netstat -an 2>nul | find /c \"ESTABLISHED\"");
    if (!result.empty()) {
        int count = 0;
        if (sscanf(result.c_str(), "%d", &count) == 1) {
            return count;
        }
    }
    return 0;
#else
    std::string result = exec("ss -tan 2>/dev/null | grep ESTAB | wc -l");
    if (!result.empty()) {
        int count = 0;
        if (sscanf(result.c_str(), "%d", &count) == 1) {
            return count;
        }
    }
    return 0;
#endif
}
