package com.nodetrace.services;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;
import java.util.stream.Collectors;

import com.google.gson.JsonObject;
import com.nodetrace.utils.Logger;

import oshi.SystemInfo;
import oshi.hardware.CentralProcessor;
import oshi.hardware.GlobalMemory;
import oshi.hardware.HWDiskStore;
import oshi.hardware.NetworkIF;
import oshi.software.os.OSProcess;
import oshi.software.os.OperatingSystem;

public class TelemetryService {

    private final SystemInfo systemInfo = new SystemInfo();
    private final CentralProcessor cpu = systemInfo.getHardware().getProcessor();
    private final OperatingSystem osSystem = systemInfo.getOperatingSystem();
    private long[] prevTicks = cpu.getSystemCpuLoadTicks();

    public JsonObject collectTelemetry(NetworkService networkService) {
        JsonObject json = new JsonObject();

        GlobalMemory memory = systemInfo.getHardware().getMemory();

        // CPU LOAD FIX
        double cpuLoad = cpu.getSystemCpuLoadBetweenTicks(prevTicks) * 100;
        prevTicks = cpu.getSystemCpuLoadTicks();

        double ramUsage = ((double)(memory.getTotal() - memory.getAvailable()) / memory.getTotal()) * 100;

        // Get network info
        JsonObject networkInfo = networkService.collectNetworkInfo();
        String publicIp = networkService.getPublicIp();

        json.addProperty("cpu_usage", cpuLoad);
        json.addProperty("ram_usage", ramUsage);
        json.addProperty("ip_local", networkInfo.get("local_ip").getAsString()); 
        json.addProperty("ip_public", publicIp != null ? publicIp : "unknown"); 
        json.addProperty("geo_country", (String)null);
        json.addProperty("geo_city", (String)null);
        json.add("processes", getTopProcesses());
        json.addProperty("disk_free", getDiskFree());
        json.addProperty("disk_total", getDiskTotal());
        json.addProperty("network_sent", getNetworkSent());
        json.addProperty("network_received", getNetworkReceived());
        json.addProperty("active_connections", getActiveConnections());

        return json;
    }

    private long getDiskFree() {
        List<HWDiskStore> disks = systemInfo.getHardware().getDiskStores();
        return disks.stream().mapToLong(d -> d.getSize() - d.getWriteBytes()).sum() / (1024 * 1024);
    }

    private long getDiskTotal() {
        List<HWDiskStore> disks = systemInfo.getHardware().getDiskStores();
        return disks.stream().mapToLong(HWDiskStore::getSize).sum() / (1024 * 1024);
    }

    private long getNetworkSent() {
        List<NetworkIF> networks = systemInfo.getHardware().getNetworkIFs();
        return networks.stream().mapToLong(NetworkIF::getBytesSent).sum();
    }

    private long getNetworkReceived() {
        List<NetworkIF> networks = systemInfo.getHardware().getNetworkIFs();
        return networks.stream().mapToLong(NetworkIF::getBytesRecv).sum();
    }

    private int getActiveConnections() {
        try {
            // Windows: use netstat command
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                int count = executeCommand("netstat -an | find /c \"ESTABLISHED\"").size();
                return count;
            } else {
                // Linux/Mac: use ss or netstat
                int count = executeCommand("ss -tan | grep ESTAB | wc -l").size();
                return count;
            }
        } catch (RuntimeException e) {
            Logger.error("Failed to get active connections: " + e.getMessage());
            return 0;
        }
    }

    private List<String> executeCommand(String command) {
        try {
            ProcessBuilder pb;
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                pb = new ProcessBuilder("cmd.exe", "/c", command);
            } else {
                pb = new ProcessBuilder("sh", "-c", command);
            }
            Process process = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            return reader.lines().collect(Collectors.toList());
        } catch (java.io.IOException e) {
            return List.of();
        }
    }

    private com.google.gson.JsonArray getTopProcesses() {
        com.google.gson.JsonArray array = new com.google.gson.JsonArray();
        try {
            List<OSProcess> processes = osSystem.getProcesses();
            processes.stream()
                    .limit(5)
                    .forEach(p -> array.add(p.getName() + " (" + p.getProcessID() + ")"));
        } catch (Exception e) {
            // Fallback if process listing fails
            array.add("Process data unavailable");
        }
        return array;
    }

    public String getCpuModel() {
        return cpu.getProcessorIdentifier().getName();
    }

    public long getTotalRamMB() {
        GlobalMemory memory = systemInfo.getHardware().getMemory();
        return memory.getTotal() / (1024 * 1024);
    }
}