package com.nodetrace.services;

import com.google.gson.JsonObject;

import oshi.SystemInfo;
import oshi.hardware.CentralProcessor;
import oshi.hardware.GlobalMemory;
import oshi.hardware.HWDiskStore;
import oshi.hardware.NetworkIF;
import oshi.software.os.OperatingSystem;
import oshi.software.os.OSProcess;
import java.util.List;
import java.util.stream.Collectors;

public class TelemetryService {

    private final SystemInfo systemInfo = new SystemInfo();
    private final CentralProcessor cpu = systemInfo.getHardware().getProcessor();
    private final OperatingSystem os = systemInfo.getOperatingSystem();
    private long[] prevTicks = cpu.getSystemCpuLoadTicks();

    public JsonObject collectTelemetry() {
        JsonObject json = new JsonObject();

        GlobalMemory memory = systemInfo.getHardware().getMemory();

        // CPU LOAD FIX
        double cpuLoad = cpu.getSystemCpuLoadBetweenTicks(prevTicks) * 100;
        prevTicks = cpu.getSystemCpuLoadTicks();

        double ramUsage = ((double)(memory.getTotal() - memory.getAvailable()) / memory.getTotal()) * 100;

        json.addProperty("cpu_usage", cpuLoad);
        json.addProperty("ram_usage", ramUsage);
        json.addProperty("ip_local", ""); 
        json.addProperty("ip_public", ""); 
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
        // OSHI doesn't have direct active connections, placeholder
        return 0;
    }

    private com.google.gson.JsonArray getTopProcesses() {
        com.google.gson.JsonArray array = new com.google.gson.JsonArray();
        List<OSProcess> processes = os.getProcesses(5, OperatingSystem.ProcessSort.CPU);
        for (OSProcess p : processes) {
            array.add(p.getName() + " (" + p.getProcessID() + ")");
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
}