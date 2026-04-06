using NodeTraceAgent.Services;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("NodeTrace Agent C# starting...");

        var agent = new AgentService();
        await agent.StartAsync();
    }
}