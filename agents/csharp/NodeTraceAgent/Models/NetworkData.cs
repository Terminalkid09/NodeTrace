namespace NodeTraceAgent.Models
{
    public class NetworkData
    {
        public string? LocalIp { get; set; }
        public string? PublicIp { get; set; }
        public string? Gateway { get; set; }
        public string? Dns { get; set; }
        public string? MacAddress { get; set; }
        public string? InterfaceName { get; set; }
    }
}