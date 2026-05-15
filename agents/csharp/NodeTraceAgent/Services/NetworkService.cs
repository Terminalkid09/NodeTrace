using System.Net;
using System.Net.NetworkInformation;
using NodeTraceAgent.Models;

namespace NodeTraceAgent.Services
{
    public class NetworkService
    {
        public NetworkData GetNetworkInfo()
        {
            var interfaces = NetworkInterface.GetAllNetworkInterfaces()
                .Where(i => i.OperationalStatus == OperationalStatus.Up &&
                            i.NetworkInterfaceType != NetworkInterfaceType.Loopback)
                .ToList();

            var primary = interfaces.FirstOrDefault();

            if (primary == null)
                return new NetworkData();

            var ipProps = primary.GetIPProperties();

            var localIp = ipProps.UnicastAddresses
                .FirstOrDefault(a => a.Address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)?
                .Address.ToString();

            var gateway = ipProps.GatewayAddresses
                .FirstOrDefault()?.Address.ToString();

            var dns = ipProps.DnsAddresses
                .FirstOrDefault()?.ToString();

            var mac = string.Join(":", primary.GetPhysicalAddress()
                .GetAddressBytes()
                .Select(b => b.ToString("X2")));

            return new NetworkData
            {
                LocalIp = localIp,
                Gateway = gateway,
                Dns = dns,
                MacAddress = mac,
                InterfaceName = primary.Name
            };
        }

        public async Task<string?> GetPublicIp()
        {
            try
            {
                using var client = new HttpClient();
                return await client.GetStringAsync("https://api.ipify.org");
            }
            catch
            {
                return null;
            }
        }
    }
}