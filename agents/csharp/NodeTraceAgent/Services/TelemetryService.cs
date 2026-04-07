using System.Diagnostics;
using System.Net.NetworkInformation;
using System.IO;
using System.Linq;

namespace NodeTraceAgent.Services
{
    public class TelemetryService
    {
        private readonly PerformanceCounter _cpuCounter;
        private readonly PerformanceCounter _ramCounter;

        public TelemetryService()
        {
            // Nota: PerformanceCounter è Windows-only. Questo agente è ottimizzato per Windows.
            // TODO: PerformanceCounter è Windows-only, add cross-platform alternative
            _cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
            _ramCounter = new PerformanceCounter("Memory", "Available MBytes");
        }

        public TelemetryData GetTelemetry(NetworkData network)
        {
            float cpu = _cpuCounter.NextValue();
            float availableRam = _ramCounter.NextValue();
            float totalRam = GetTotalRamMB();
            float ramUsage = ((totalRam - availableRam) / totalRam) * 100;

            var disk = GetDiskInfo();
            var networkStats = GetNetworkStats();
            var processes = GetTopProcesses();

            return new TelemetryData
            {
                CpuUsage = cpu,
                RamUsage = ramUsage,
                IpLocal = network.LocalIp,
                IpPublic = network.PublicIp,
                GeoCountry = null, // TODO
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
                var network = new PerformanceCounter("Network Interface", "Bytes Sent/sec", GetNetworkInterface());
                var sent = (int)network.NextValue();
                network.CounterName = "Bytes Received/sec";
                var received = (int)network.NextValue();
                return (sent, received);
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
                    .OrderByDescending(p => p.TotalProcessorTime.TotalMilliseconds)
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
                return (float)new Microsoft.VisualBasic.Devices.ComputerInfo().TotalPhysicalMemory / (1024 * 1024);
            }
            catch
            {
                return 0;
            }
        }
    }
}