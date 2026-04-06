using System.Text.Json;

namespace NodeTraceAgent.Services
{
    public record TokenData(string Token, string DeviceId);

    public class TokenService
    {
        private readonly string _path = "token.json";

        public void SaveToken(string token, string deviceId)
        {
            var data = new { Token = token, DeviceId = deviceId };
            var json = JsonSerializer.Serialize(data);
            File.WriteAllText(_path, json);
        }

        public (string? Token, string? DeviceId) LoadToken()
        {
            if (!File.Exists(_path))
                return (null, null);

            var json = File.ReadAllText(_path);
            var data = JsonSerializer.Deserialize<TokenData>(json);
            return (data?.Token, data?.DeviceId);
        }
    }
}