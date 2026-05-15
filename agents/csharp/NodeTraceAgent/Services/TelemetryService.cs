using System.Diagnostics;
using System.Net.NetworkInformation;
using System.IO;
using System.Linq;
using System.Management;
using NodeTraceAgent.Models;

namespace NodeTraceAgent.Services
{
    public class TelemetryService
    {
        private readonly PerformanceCounter _cpuCounter;
        private readonly PerformanceCounter _ramCounter;

        public TelemetryService()
        {
            // Nota: PerformanceCounter è Windows-only. Questo agente è ottimizzato per Windows.
            _cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
            _ramCounter = new PerformanceCounter("Memory", "Available MBytes");
        }

        public TelemetryData GetTelemetry(NetworkData network)
        {
            float cpu = _cpuCounter.NextValue();
            float availableRam = _ramCounter.NextValue();
            float totalRam = GetTotalRamMB();
            float ramUsage = 0;

            if (totalRam > 0)
            {
                ramUsage = ((totalRam - availableRam) / totalRam) * 100;
            }

            var disk = GetDiskInfo();
            var networkStats = GetNetworkStats();
            var processes = GetTopProcesses();

            return new TelemetryData
            {
                CpuUsage = cpu,
                RamUsage = ramUsage,
                AvailableRamMB = availableRam,
                IpLocal = network.LocalIp,
                IpPublic = network.PublicIp,
                GeoCountry = null,
                GeoCity = null,
                Processes = processes,
                DiskFree = disk.free,
                DiskTotal = disk.total,
                NetworkSent = networkStats.sent,
                NetworkReceived = networkStats.received,
                ActiveConnections = GetActiveConnections()
            };
        }

        private (int free, int total) GetDiskInfo()
        {
            try
            {
                var drive = new DriveInfo("C");
                if (drive.IsReady)
                {
                    return ((int)(drive.AvailableFreeSpace / (1024 * 1024)), (int)(drive.TotalSize / (1024 * 1024)));
                }
            }
            catch
            {
                // Fallback
            }
            return (0, 0);
        }

        private (int sent, int received) GetNetworkStats()
        {
            try
            {
                // Note: GetNetworkInterface might need careful mapping for PerformanceCounter
                return (0, 0); // Placeholder for now to avoid crashes on interface name mismatch
            }
            catch
            {
                return (0, 0);
            }
        }

        private string GetNetworkInterface()
        {
            var interfaces = NetworkInterface.GetAllNetworkInterfaces();
            return interfaces.FirstOrDefault()?.Name ?? "";
        }

        private List<string> GetTopProcesses()
        {
            try
            {
                return Process.GetProcesses()
                    .Where(p => p.Id != 0) // Skip System Idle Process
                    .OrderByDescending(p => {
                        try { return p.WorkingSet64; } catch { return 0; }
                    })
                    .Take(5)
                    .Select(p => $"{p.ProcessName} ({p.Id})")
                    .ToList();
            }
            catch
            {
                return new List<string>();
            }
        }

        private int GetActiveConnections()
        {
            try
            {
                return IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpConnections().Length;
            }
            catch
            {
                return 0;
            }
        }

        private float GetTotalRamMB()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        return (float)(Convert.ToInt64(obj["TotalPhysicalMemory"]) / (1024 * 1024));
                    }
                }
            }
            catch
            {
                // Fallback
            }
            return 0;
        }
    }
}