package com.nodetrace.services;

import com.nodetrace.utils.Logger;

public class RetryPolicy {

    private final int maxAttempts;
    private final int baseDelayMs;

    public RetryPolicy(int maxAttempts, int baseDelayMs) {
        this.maxAttempts = maxAttempts;
        this.baseDelayMs = baseDelayMs;
    }

    public void execute(Runnable action) throws Exception {
        int attempt = 1;

        while (true) {
            try {
                action.run();
                return;
            } catch (Exception e) {
                if (attempt >= maxAttempts) {
                    Logger.error("RetryPolicy: max attempts reached.");
                    throw e;
                }

                int delay = baseDelayMs * attempt;
                Logger.warn("Retry attempt " + attempt + " failed. Retrying in " + delay + "ms...");
                Thread.sleep(delay);
                attempt++;
            }
        }
    }
}