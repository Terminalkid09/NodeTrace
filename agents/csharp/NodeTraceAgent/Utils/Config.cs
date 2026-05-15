using System.Text.Json;

namespace NodeTraceAgent.Utils
{
    public class ConfigData
    {
        public string DeviceName { get; set; } = "";
        public string RegisterUrl { get; set; } = "";
        public string UpdateUrl { get; set; } = "";
        public string HeartbeatUrl { get; set; } = "";
        public int HeartbeatInterval { get; set; }
        public int RetryMaxAttempts { get; set; }
        public int RetryBaseDelay { get; set; }
        public string EnrollKey { get; set; } = "";
    }

    public class Config
    {
        private readonly ConfigData _data;

        public string DeviceName => _data.DeviceName;
        public string RegisterUrl => _data.RegisterUrl;
        public string UpdateUrl => _data.UpdateUrl;
        public string HeartbeatUrl => _data.HeartbeatUrl;
        public int HeartbeatInterval => _data.HeartbeatInterval;
        public int RetryMaxAttempts => _data.RetryMaxAttempts;
        public int RetryBaseDelay => _data.RetryBaseDelay;
        public string EnrollKey => _data.EnrollKey;

        public Config()
        {
            _data = new ConfigData();
            try
            {
                string configPath = "config.json";
                if (!File.Exists(configPath))
                {
                    string baseDir = AppDomain.CurrentDomain.BaseDirectory;
                    configPath = Path.Combine(baseDir, "config.json");
                }
                
                if (!File.Exists(configPath))
                {
                    configPath = "agents/csharp/NodeTraceAgent/config.json";
                }

                if (File.Exists(configPath))
                {
                    var json = File.ReadAllText(configPath);
                    var cfg = JsonSerializer.Deserialize<ConfigData>(json);

                    if (cfg != null)
                    {
                        _data = cfg;
                    }
                }
                else
                {
                    Console.WriteLine("ERROR: config.json not found.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: Failed to load configuration: {ex.Message}");
            }
        }
    }
}
