# NodeTrace Frontend

The NodeTrace frontend is a lightweight, real‑time monitoring dashboard that visualizes device status, telemetry, and alerts collected by the NodeTrace backend. It provides a clean and responsive interface for interacting with the platform’s REST API.

---

## Overview

This dashboard acts as the presentation layer of the NodeTrace ecosystem.  
It consumes the backend APIs to display:

- Device availability and heartbeat status  
- Real‑time CPU and RAM telemetry  
- Detailed device information  
- Active alerts with severity indicators  
- Auto‑refreshing data every few seconds  

The frontend is fully static and requires no build tools or frameworks.

---

## Features

### ✔ Device Monitoring
- Displays all registered devices  
- Online/offline status  
- Last heartbeat timestamp  
- Clickable rows to select a device  

### ✔ Device Detail Panel
Shows detailed information for the selected device, including:
- Name  
- Operating system  
- OS version  
- CPU model  
- Total RAM  
- Last seen timestamp  

### ✔ Real‑Time Telemetry
- CPU usage chart  
- RAM usage chart  
- Charts update every 5 seconds  
- Keeps a rolling history of the last 20 samples  

### ✔ Alerts System
- Fetches active alerts from the backend  
- Severity‑based color coding (info, warning, critical)  
- Displays message, device ID, and timestamp  

### ✔ Auto‑Refresh
All dashboard sections update automatically every 5 seconds:
- Status overview  
- Device list  
- Alerts  
- Telemetry for the selected device  

---

## Project Structure

```text
frontend/
├── assets/            # Static images and icons (optional)
├── dashboard.js       # Main logic: API calls, charts, UI updates
├── index.html         # Dashboard entry point
├── README.md          # Frontend documentation
└── style.css          # Dashboard styling and layout
```
---

## Setup
- Start the NodeTrace backend and ensure it is reachable at http://localhost:8000
- Launch at least one agent (Python, C#, Java, or C++ placeholder).
- Open frontend/index.html
- If needed, adjust API URLs inside dashboard.js

---

### Development Notes

- dashboard.js handles all API communication, telemetry updates and DOM rendering.
- style.css defines the layout, card styling, table formatting and alert colors.
- The dashboard is intentionally simple and framework-free for portability and clarity.
- Additional UI improvements or themes can be added easily.
