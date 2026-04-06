using System.Text.Json;

namespace NodeTraceAgent.Utils
{
    public class Config
    {
        public string DeviceName { get; set; } = "";
        public string RegisterUrl { get; set; } = "";
        public string UpdateUrl { get; set; } = "";
        public string HeartbeatUrl { get; set; } = "";
        public int HeartbeatInterval { get; set; }
        public int RetryMaxAttempts { get; set; }
        public int RetryBaseDelay { get; set; }
        public string EnrollKey { get; set; } = "";

        public Config()
        {
            try
            {
                var json = File.ReadAllText("config.json");
                var cfg = JsonSerializer.Deserialize<Config>(json);

                if (cfg != null)
                {
                    DeviceName = cfg.DeviceName;
                    RegisterUrl = cfg.RegisterUrl;
                    UpdateUrl = cfg.UpdateUrl;
                    HeartbeatUrl = cfg.HeartbeatUrl;
                    HeartbeatInterval = cfg.HeartbeatInterval;
                    RetryMaxAttempts = cfg.RetryMaxAttempts;
                    RetryBaseDelay = cfg.RetryBaseDelay;
                    EnrollKey = cfg.EnrollKey;
                }
            }
            catch
            {
                Console.WriteLine("ERROR: Failed to load config.json");
            }
        }
    }
}