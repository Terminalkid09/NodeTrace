using System.Net.Http;
using System.Net.Http.Json;
using NodeTraceAgent.Models;
using NodeTraceAgent.Utils;
using System.Management;

namespace NodeTraceAgent.Services
{
    public class AgentService
    {
        private readonly HttpClient _http = new HttpClient();
        private readonly Config _config = new Config();

        private readonly TelemetryService _telemetry = new TelemetryService();
        private readonly NetworkService _network = new NetworkService();
        private readonly TokenService _tokenService = new TokenService();

        public async Task StartAsync()
        {
            Logger.Info("Starting agent...");

            // Prova a caricare il token salvato precedentemente
            var (savedToken, savedDeviceId) = _tokenService.LoadToken();

            if (savedToken != null && savedDeviceId != null)
            {
                Logger.Info("Loaded saved token.");
                await RunHeartbeatLoop(savedToken, savedDeviceId);
                return;
            }

            // Altrimenti registra il device
            Logger.Info("Registering device...");
            var device = await RegisterDevice();

            if (device == null || device.Token == null || device.DeviceId == null)
            {
                Logger.Error("Failed to register device.");
                return;
            }

            Logger.Info($"Device registered. Token: {device.Token}");

            // Salva il token
            _tokenService.SaveToken(device.Token, device.DeviceId);

            // Avvia heartbeat
            await RunHeartbeatLoop(device.Token, device.DeviceId);
        }

        private async Task<DeviceResponse?> RegisterDevice()
        {
            return await RetryPolicy.ExecuteWithRetry(async () =>
            {
                var network = _network.GetNetworkInfo();

                // Collect system info
                string osVersion = Environment.OSVersion.Version.ToString();
                string cpuModel = GetCpuModel();
                int totalRam = GetTotalRamMB();

                var payload = new
                {
                    hostname = _config.DeviceName,
                    os = Environment.OSVersion.ToString(),
                    os_version = osVersion,
                    cpu_model = cpuModel,
                    total_ram = totalRam,
                    mac_address = network.MacAddress,
                    enroll_key = _config.EnrollKey
                };

                var response = await _http.PostAsJsonAsync(_config.RegisterUrl, payload);

                if (!response.IsSuccessStatusCode)
                    throw new Exception($"HTTP {response.StatusCode}");

                return await response.Content.ReadFromJsonAsync<DeviceResponse>();
            });
        }

        private string GetCpuModel()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Name FROM Win32_Processor"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        return obj["Name"].ToString();
                    }
                }
            }
            catch
            {
                // Fallback
            }
            return "Unknown";
        }

        private int GetTotalRamMB()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        return (int)(Convert.ToInt64(obj["TotalPhysicalMemory"]) / (1024 * 1024));
                    }
                }
            }
            catch
            {
                // Fallback
            }
            return 0;
        }

        private async Task SendTelemetry(string token, string deviceId)
        {
            await RetryPolicy.ExecuteWithRetry(async () =>
            {
                var network = _network.GetNetworkInfo();
                network.PublicIp = await _network.GetPublicIp();
                var telemetry = _telemetry.GetTelemetry(network);

                var payload = new
                {
                    device_id = deviceId,
                    cpu_usage = telemetry.CpuUsage,
                    ram_usage = telemetry.RamUsage,
                    ip_local = telemetry.IpLocal,
                    ip_public = telemetry.IpPublic,
                    geo_country = telemetry.GeoCountry,
                    geo_city = telemetry.GeoCity,
                    processes = telemetry.Processes,
                    disk_free = telemetry.DiskFree,
                    disk_total = telemetry.DiskTotal,
                    network_sent = telemetry.NetworkSent,
                    network_received = telemetry.NetworkReceived,
                    active_connections = telemetry.ActiveConnections
                };

                var request = new HttpRequestMessage(HttpMethod.Post, _config.UpdateUrl);
                request.Headers.Add("Authorization", $"Bearer {token}");
                request.Content = JsonContent.Create(payload);

                var response = await _http.SendAsync(request);

                Logger.Info(
                    $"Telemetry: {response.StatusCode} | CPU: {telemetry.CpuUsage}% | RAM: {telemetry.AvailableRamMB}MB"
                );

                return true;
            });
        }

        private async Task SendHeartbeat(string deviceId)
        {
            await RetryPolicy.ExecuteWithRetry(async () =>
            {
                var payload = new
                {
                    device_id = deviceId
                };

                var response = await _http.PostAsJsonAsync(_config.HeartbeatUrl, payload);

                Logger.Info($"Heartbeat: {response.StatusCode}");

                return true;
            });
        }

        private async Task RunHeartbeatLoop(string token, string deviceId)
        {
            while (true)
            {
                await SendTelemetry(token, deviceId);
                await SendHeartbeat(deviceId);
                await Task.Delay(_config.HeartbeatInterval * 1000);
            }
        }
    }
}