package com.nodetrace.services;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.util.Enumeration;

import com.google.gson.JsonObject;
import com.nodetrace.utils.Logger;

public class NetworkService {

    public JsonObject collectNetworkInfo() {
        JsonObject json = new JsonObject();

        try {
            InetAddress local = InetAddress.getLocalHost();
            json.addProperty("local_ip", local.getHostAddress());
            json.addProperty("hostname", local.getHostName());

            // Get MAC address
            String macAddress = getMacAddress();
            json.addProperty("mac_address", macAddress);
        } catch (java.net.UnknownHostException e) {
            Logger.error("Failed to get network info: " + e.getMessage());
            json.addProperty("local_ip", "unknown");
            json.addProperty("hostname", "unknown");
            json.addProperty("mac_address", "unknown");
        }

        return json;
    }

    public String getPublicIp() {
        try {
            java.net.URL url = new java.net.URL("https://api.ipify.org");
            try (BufferedReader br = new BufferedReader(new InputStreamReader(url.openStream()))) {
                return br.readLine();
            }
        } catch (java.io.IOException e) {
            Logger.error("Failed to get public IP: " + e.getMessage());
            return null;
        }
    }

    private String getMacAddress() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface ni = interfaces.nextElement();
                if (!ni.isLoopback() && ni.isUp()) {
                    byte[] mac = ni.getHardwareAddress();
                    if (mac != null) {
                        StringBuilder sb = new StringBuilder();
                        for (int i = 0; i < mac.length; i++) {
                            sb.append(String.format("%02X%s", mac[i], (i < mac.length - 1) ? ":" : ""));
                        }
                        return sb.toString();
                    }
                }
            }
        } catch (java.net.SocketException e) {
            Logger.error("Failed to get MAC address: " + e.getMessage());
        }
        return "unknown";
    }
}