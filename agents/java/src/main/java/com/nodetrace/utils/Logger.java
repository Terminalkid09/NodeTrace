package com.nodetrace.utils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class Logger {

    private static final DateTimeFormatter formatter =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void info(String message) {
        System.out.println("[INFO] " + timestamp() + " - " + message);
    }

    public static void error(String message) {
        System.err.println("[ERROR] " + timestamp() + " - " + message);
    }

    public static void warn(String message) {
        System.out.println("[WARN] " + timestamp() + " - " + message);
    }

    private static String timestamp() {
        return LocalDateTime.now().format(formatter);
    }
}