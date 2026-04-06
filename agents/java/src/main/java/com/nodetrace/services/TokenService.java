package com.nodetrace.services;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.nodetrace.utils.Logger;

public class TokenService {

    private static final String TOKEN_FILE = "token.json";
    private final Gson gson = new Gson();

    public String loadToken() {
        try (FileReader reader = new FileReader(TOKEN_FILE)) {
            JsonObject json = gson.fromJson(reader, JsonObject.class);
            return json.get("token").getAsString();
        } catch (Exception e) {
            Logger.warn("Token not found, will request a new one.");
            return null;
        }
    }

    public String loadDeviceId() {
        try (FileReader reader = new FileReader(TOKEN_FILE)) {
            JsonObject json = gson.fromJson(reader, JsonObject.class);
            return json.get("device_id").getAsString();
        } catch (Exception e) {
            return null;
        }
    }

    public void saveToken(String token, String deviceId) {
        try (FileWriter writer = new FileWriter(TOKEN_FILE)) {
            JsonObject json = new JsonObject();
            json.addProperty("token", token);
            json.addProperty("device_id", deviceId);
            writer.write(gson.toJson(json));
            Logger.info("Token saved.");
        } catch (IOException e) {
            Logger.error("Failed to save token: " + e.getMessage());
        }
    }
}