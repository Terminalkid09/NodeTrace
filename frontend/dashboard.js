let selectedDevice = null;

let cpuChart = null;
let ramChart = null;

function initCharts() {
    const cpuCtx = document.getElementById("cpuChart").getContext("2d");
    const ramCtx = document.getElementById("ramChart").getContext("2d");

    cpuChart = new Chart(cpuCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "CPU %",
                data: [],
                borderColor: "red",
                tension: 0.2
            }]
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
                tension: 0.2
            }]
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

    } catch (error) {
        console.error("Telemetry error:", error);
    }
}

// Carica le informazioni del device selezionato
async function loadDeviceInfo() {
    if (!selectedDevice) {
        document.getElementById("device-details").innerHTML =
            "<p>Nessun device selezionato</p>";
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/devices/${selectedDevice}`);
        const device = await response.json();

        document.getElementById("device-details").innerHTML = `
            <p><strong>Nome:</strong> ${device.name}</p>
            <p><strong>OS:</strong> ${device.os}</p>
            <p><strong>Versione OS:</strong> ${device.os_version}</p>
            <p><strong>CPU:</strong> ${device.cpu_model}</p>
            <p><strong>RAM Totale:</strong> ${device.total_ram} MB</p>
            <p><strong>Ultimo heartbeat:</strong> ${device.last_seen}</p>
        `;

    } catch (error) {
        console.error("Errore caricamento info device:", error);
    }
}

// Aggiorna ogni 5 secondi
setInterval(loadTelemetry, 5000);

async function loadDevices() {
    try {
        const response = await fetch("http://localhost:8000/devices");
        const devices = await response.json();

        const table = document.getElementById("device-table");
        table.innerHTML = ""; // pulizia tabella

        devices.forEach(device => {

            const row = document.createElement("tr");

            const status = `
                    <span class="status-badge ${device.status}">
                        ${device.status === "online" ? "Online" : "Offline"}
                    </span>
            `;

            row.innerHTML = `
                <td>${device.id}</td>
                <td>${device.name}</td>
                <td>${status}</td>
                <td>${device.last_seen}</td>
            `;

            // Mantieni evidenziato il device selezionato
            if (device.id === selectedDevice) {
                row.classList.add("selected-row");
            }

            // Selezione device
            row.addEventListener("click", () => {
                selectedDevice = device.id;

                // Rimuovi selezione da tutte le righe
                document.querySelectorAll("#device-table tr").forEach(r => {
                    r.classList.remove("selected-row");
                });

                // Evidenzia la riga cliccata
                row.classList.add("selected-row");

                loadTelemetry(); // aggiorna subito i grafici
                loadDeviceInfo(); // aggiorna subito le informazioni del device
            });

            table.appendChild(row);
        });

    } catch (error) {
        console.error("Telemetry error:", error);
    }
}

// Avvio + aggiornamento ogni 5 secondi
loadDevices();
setInterval(loadDevices, 5000);

async function loadAlerts() {
    try {
        const response = await fetch("http://localhost:8000/alerts");
        const alerts = await response.json();

        const container = document.getElementById("alert-list");
        container.innerHTML = "";

        if (alerts.length === 0) {
            container.innerHTML = "<p>Nessun alert attivo</p>";
            return;
        }

        alerts.forEach(alert => {
            const div = document.createElement("div");
            div.classList.add("alert-item");

            // Colore in base alla severity dell'alert
            if (alert.severity === "critical") div.classList.add("alert-critical");
            else if (alert.severity === "warning") div.classList.add("alert-warning");
            else div.classList.add("alert-info");

            div.innerHTML = `
                <p><strong>${alert.severity.toUpperCase()}</strong> — ${alert.message}</p>
                <p><small>Device: ${alert.device_id} | ${alert.timestamp}</small></p>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        console.error("Errore caricamento alert:", error);
    }
}

// Aggiorna ogni 5 secondi
loadAlerts();
setInterval(loadAlerts, 5000);