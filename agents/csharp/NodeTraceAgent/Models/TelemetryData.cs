namespace NodeTraceAgent.Models
{
    public class TelemetryData
    {
        public float CpuUsage { get; set; }
        public float RamUsage { get; set; }
        public float AvailableRamMB { get; set; }
        public string? IpLocal { get; set; }
        public string? IpPublic { get; set; }
        public string? GeoCountry { get; set; }
        public string? GeoCity { get; set; }
        public List<string>? Processes { get; set; }
        public int? DiskFree { get; set; }
        public int? DiskTotal { get; set; }
        public int? NetworkSent { get; set; }
        public int? NetworkReceived { get; set; }
        public int? ActiveConnections { get; set; }
    }
}