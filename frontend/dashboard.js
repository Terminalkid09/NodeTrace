let selectedDevice = null;

let cpuChart = null;
let ramChart = null;
let diskChart = null;
let networkChart = null;

function initCharts() {
    const cpuCtx = document.getElementById("cpuChart").getContext("2d");
    const ramCtx = document.getElementById("ramChart").getContext("2d");
    const diskCtx = document.getElementById("diskChart").getContext("2d");
    const networkCtx = document.getElementById("networkChart").getContext("2d");

    cpuChart = new Chart(cpuCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "CPU %",
                data: [],
                borderColor: "red",
                backgroundColor: "rgba(255, 0, 0, 0.1)",
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    ramChart = new Chart(ramCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "RAM %",
                data: [],
                borderColor: "blue",
                backgroundColor: "rgba(0, 0, 255, 0.1)",
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    diskChart = new Chart(diskCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Disk Free (MB)",
                data: [],
                borderColor: "green",
                backgroundColor: "rgba(0, 255, 0, 0.1)",
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    networkChart = new Chart(networkCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Network Sent (Bytes)",
                    data: [],
                    borderColor: "orange",
                    backgroundColor: "rgba(255, 165, 0, 0.1)",
                    tension: 0.2
                },
                {
                    label: "Network Received (Bytes)",
                    data: [],
                    borderColor: "purple",
                    backgroundColor: "rgba(128, 0, 128, 0.1)",
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

initCharts();

async function loadTelemetry() {
    if (!selectedDevice) return;

    try {
        const response = await fetch(`http://localhost:8000/telemetry/${selectedDevice}`);
        const data = await response.json();

        const timestamp = new Date().toLocaleTimeString();

        // CPU
        cpuChart.data.labels.push(timestamp);
        cpuChart.data.datasets[0].data.push(data.cpu_usage);
        if (cpuChart.data.labels.length > 20) {
            cpuChart.data.labels.shift();
            cpuChart.data.datasets[0].data.shift();
        }
        cpuChart.update();

        // RAM
        ramChart.data.labels.push(timestamp);
        ramChart.data.datasets[0].data.push(data.ram_usage);
        if (ramChart.data.labels.length > 20) {
            ramChart.data.labels.shift();
            ramChart.data.datasets[0].data.shift();
        }
        ramChart.update();

        // Disk
        diskChart.data.labels.push(timestamp);
        diskChart.data.datasets[0].data.push(data.disk_free || 0);
        if (diskChart.data.labels.length > 20) {
            diskChart.data.labels.shift();
            diskChart.data.datasets[0].data.shift();
        }
        diskChart.update();

        // Network
        networkChart.data.labels.push(timestamp);
        networkChart.data.datasets[0].data.push(data.network_sent || 0);
        networkChart.data.datasets[1].data.push(data.network_received || 0);
        if (networkChart.data.labels.length > 20) {
            networkChart.data.labels.shift();
            networkChart.data.datasets[0].data.shift();
            networkChart.data.datasets[1].data.shift();
        }
        networkChart.update();

        // Real-time telemetry cards
        document.getElementById("ip-local").textContent = data.ip_local || "--";
        document.getElementById("ip-public").textContent = data.ip_public || "--";
        document.getElementById("disk-free").textContent = data.disk_free || "--";
        document.getElementById("disk-total").textContent = data.disk_total || "--";
        document.getElementById("network-sent").textContent = data.network_sent || "--";
        document.getElementById("network-received").textContent = data.network_received || "--";
        document.getElementById("active-connections").textContent = data.active_connections || "--";

        // Processes
        if (data.processes && Array.isArray(data.processes)) {
            const processList = document.getElementById("processes-list");
            processList.innerHTML = data.processes.map(p => `<p>${p}</p>`).join("");
        }

    } catch (error) {
        console.error("Telemetry error:", error);
    }
}

// Load device info with MAC address
async function loadDeviceInfo() {
    if (!selectedDevice) {
        document.getElementById("device-details").innerHTML =
            "<p>No device selected</p>";
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/devices/${selectedDevice}`);
        const device = await response.json();

        document.getElementById("device-details").innerHTML = `
            <p><strong>Hostname:</strong> ${device.hostname}</p>
            <p><strong>MAC Address:</strong> ${device.mac_address || "--"}</p>
            <p><strong>OS:</strong> ${device.os}</p>
            <p><strong>OS Version:</strong> ${device.os_version || "--"}</p>
            <p><strong>CPU Model:</strong> ${device.cpu_model || "--"}</p>
            <p><strong>Total RAM:</strong> ${device.total_ram || "--"} MB</p>
            <p><strong>Last Heartbeat:</strong> ${device.last_seen || "--"}</p>
        `;

        // Also update MAC in telemetry section
        document.getElementById("mac-address").textContent = device.mac_address || "--";

    } catch (error) {
        console.error("Error loading device info:", error);
    }
}

// Update every 5 seconds
setInterval(loadTelemetry, 5000);

async function loadDevices() {
    try {
        const response = await fetch("http://localhost:8000/devices");
        const devices = await response.json();

        const table = document.getElementById("device-table");
        table.innerHTML = "";

        devices.forEach(device => {
            const row = document.createElement("tr");
            const status = `
                <span class="status-badge ${device.status}">
                    ${device.status === "online" ? "Online" : "Offline"}
                </span>
            `;

            row.innerHTML = `
                <td>${device.device_id}</td>
                <td>${device.hostname}</td>
                <td>${status}</td>
                <td>${device.last_seen || "--"}</td>
            `;

            if (device.device_id === selectedDevice) {
                row.classList.add("selected-row");
            }

            row.addEventListener("click", () => {
                selectedDevice = device.device_id;
                document.querySelectorAll("#device-table tr").forEach(r => {
                    r.classList.remove("selected-row");
                });
                row.classList.add("selected-row");
                loadTelemetry();
                loadDeviceInfo();
            });

            table.appendChild(row);
        });

    } catch (error) {
        console.error("Error loading devices:", error);
    }
}

// Initial load + refresh every 5 seconds
loadDevices();
setInterval(loadDevices, 5000);

async function loadAlerts() {
    try {
        const response = await fetch("http://localhost:8000/alerts");
        const alerts = await response.json();

        const container = document.getElementById("alert-list");
        container.innerHTML = "";

        if (alerts.length === 0) {
            container.innerHTML = "<p>No active alerts</p>";
            document.getElementById("alert-count").textContent = "0";
            return;
        }

        document.getElementById("alert-count").textContent = alerts.length;

        alerts.forEach(alert => {
            const div = document.createElement("div");
            div.classList.add("alert-item");

            if (alert.severity === "critical") div.classList.add("alert-critical");
            else if (alert.severity === "warning") div.classList.add("alert-warning");
            else div.classList.add("alert-info");

            div.innerHTML = `
                <p><strong>${(alert.severity || "info").toUpperCase()}</strong> — ${alert.message || "No message"}</p>
                <p><small>Device: ${alert.device_id} | ${alert.timestamp || "N/A"}</small></p>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        console.error("Error loading alerts:", error);
    }
}

// Load alerts and status
loadAlerts();
setInterval(loadAlerts, 5000);

async function loadStatus() {
    try {
        const response = await fetch("http://localhost:8000/status");
        const status = await response.json();

        document.getElementById("online-count").textContent = status.online || 0;
        document.getElementById("offline-count").textContent = status.offline || 0;

    } catch (error) {
        console.error("Error loading status:", error);
    }
}

loadStatus();
setInterval(loadStatus, 5000);