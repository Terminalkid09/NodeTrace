package com.nodetrace;

import java.io.FileReader;
import java.util.Timer;
import java.util.TimerTask;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.nodetrace.services.NetworkService;
import com.nodetrace.services.RetryPolicy;
import com.nodetrace.services.TelemetryService;
import com.nodetrace.services.TokenService;
import com.nodetrace.utils.Logger;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class Agent {

    private JsonObject config;
    private final Gson gson = new Gson();
    private final OkHttpClient http = new OkHttpClient();

    private final TokenService tokenService = new TokenService();
    private final TelemetryService telemetryService = new TelemetryService();
    private final NetworkService networkService = new NetworkService();

    private RetryPolicy retryPolicy;

    public static void main(String[] args) {
        new Agent().start();
    }

    public void start() {
        loadConfig();

        retryPolicy = new RetryPolicy(
                config.get("retry_max_attempts").getAsInt(),
                config.get("retry_base_delay").getAsInt()
        );

        String token = tokenService.loadToken();
        String deviceId = tokenService.loadDeviceId();
        if (token == null) {
            JsonObject device = registerDevice();
            token = device.get("device_token").getAsString();
            deviceId = device.get("device_id").getAsString();
            tokenService.saveToken(token, deviceId);
        }

        startHeartbeat(token, deviceId);
    }

    private void loadConfig() {
        try (FileReader reader = new FileReader("config.json")) {
            config = gson.fromJson(reader, JsonObject.class);
            Logger.info("Config loaded.");
        } catch (Exception e) {
            Logger.error("Failed to load config.json");
            System.exit(1);
        }
    }

    private JsonObject registerDevice() {
        Logger.info("Registering device...");

        JsonObject network = networkService.collectNetworkInfo();

        // Collect system info
        String osVersion = System.getProperty("os.version");
        String cpuModel = telemetryService.getCpuModel();
        long totalRam = telemetryService.getTotalRamMB();

        JsonObject payload = new JsonObject();
        payload.addProperty("hostname", config.get("device_name").getAsString());
        payload.addProperty("os", System.getProperty("os.name") + " " + System.getProperty("os.version"));
        payload.addProperty("os_version", osVersion);
        payload.addProperty("cpu_model", cpuModel);
        payload.addProperty("total_ram", totalRam);
        payload.addProperty("mac_address", network.get("mac_address").getAsString());
        payload.addProperty("enroll_key", config.get("enroll_key").getAsString());

        RequestBody body = RequestBody.create(
                gson.toJson(payload),
                MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(config.get("register_url").getAsString())
                .post(body)
                .build();

        try {
            Response response = http.newCall(request).execute();
            String responseBody = response.body().string();

            JsonObject json = gson.fromJson(responseBody, JsonObject.class);
            return json;

        } catch (Exception e) {
            Logger.error("Registration failed: " + e.getMessage());
            System.exit(1);
            return null;
        }
    }

    private void startHeartbeat(String token, String deviceId) {
        Logger.info("Starting heartbeat loop...");

        int interval = config.get("heartbeat_interval").getAsInt() * 1000;

        new Timer().scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                sendTelemetry(token, deviceId);
                sendHeartbeat(deviceId);
            }
        }, 0, interval);
    }

    private void sendTelemetry(String token, String deviceId) {
        try {
            retryPolicy.execute(() -> {

                JsonObject telemetry = telemetryService.collectTelemetry();
                JsonObject network = networkService.collectNetworkInfo();

                JsonObject payload = new JsonObject();
                payload.addProperty("device_id", deviceId);
                payload.addProperty("cpu_usage", telemetry.get("cpu_usage").getAsDouble());
                payload.addProperty("ram_usage", telemetry.get("ram_usage").getAsDouble());
                payload.addProperty("ip_local", telemetry.get("ip_local").getAsString());
                payload.addProperty("ip_public", telemetry.get("ip_public").getAsString());
                payload.add("geo_country", telemetry.get("geo_country"));
                payload.add("geo_city", telemetry.get("geo_city"));
                payload.add("processes", telemetry.get("processes"));
                payload.addProperty("disk_free", telemetry.get("disk_free").getAsLong());
                payload.addProperty("disk_total", telemetry.get("disk_total").getAsLong());
                payload.addProperty("network_sent", telemetry.get("network_sent").getAsLong());
                payload.addProperty("network_received", telemetry.get("network_received").getAsLong());
                payload.addProperty("active_connections", telemetry.get("active_connections").getAsInt());

                RequestBody body = RequestBody.create(
                        gson.toJson(payload),
                        MediaType.parse("application/json")
                );

                Request request = new Request.Builder()
                        .url(config.get("update_url").getAsString())
                        .header("Authorization", "Bearer " + token)
                        .post(body)
                        .build();

                try (Response response = http.newCall(request).execute()) {
                    Logger.info("Telemetry sent. Status: " + response.code());
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });

        } catch (Exception e) {
            Logger.error("Telemetry failed after retries.");
        }
    }

    private void sendHeartbeat(String deviceId) {
        try {
            retryPolicy.execute(() -> {

                JsonObject payload = new JsonObject();
                payload.addProperty("device_id", deviceId);

                RequestBody body = RequestBody.create(
                        gson.toJson(payload),
                        MediaType.parse("application/json")
                );

                Request request = new Request.Builder()
                        .url(config.get("heartbeat_url").getAsString())
                        .post(body)
                        .build();

                try (Response response = http.newCall(request).execute()) {
                    Logger.info("Heartbeat sent. Status: " + response.code());
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });

        } catch (Exception e) {
            Logger.error("Heartbeat failed after retries.");
        }
    }
}