namespace NodeTraceAgent.Utils
{
    public static class RetryPolicy
    {
        public static async Task<T?> ExecuteWithRetry<T>(
            Func<Task<T>> action,
            int maxRetries = 5,
            int initialDelayMs = 1000)
        {
            int attempt = 0;
            int delay = initialDelayMs;

            while (attempt < maxRetries)
            {
                try
                {
                    return await action();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Retry] Attempt {attempt + 1}/{maxRetries} failed: {ex.Message}");
                }

                await Task.Delay(delay);
                delay *= 2; // backoff esponenziale
                attempt++;
            }

            return default;
        }
    }
}