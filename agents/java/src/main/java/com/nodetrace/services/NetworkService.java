package com.nodetrace.services;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.util.Enumeration;

import com.google.gson.JsonObject;

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
        } catch (Exception e) {
            json.addProperty("local_ip", "unknown");
            json.addProperty("hostname", "unknown");
            json.addProperty("mac_address", "unknown");
        }

        return json;
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
        } catch (Exception e) {
            // ignore
        }
        return "unknown";
    }
}