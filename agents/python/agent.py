import json
import time
import requests

from utils.logger import Logger
from services.telemetry import TelemetryService
from services.network import NetworkService
from services.token_service import TokenService
from services.retry_policy import retry

class Agent:
    def __init__(self):
        with open("config.json") as f:
            self.config = json.load(f)

        self.telemetry = TelemetryService()
        self.network = NetworkService()
        self.token_service = TokenService()

    @retry(5, 1)
    def register(self):
        network = self.network.get()

        # Collect system info
        system_info = self.telemetry.get_system_info()

        payload = {
            "hostname": self.config["device_name"],
            "os": system_info["os"],
            "os_version": system_info["os_version"],
            "cpu_model": system_info["cpu_model"],
            "total_ram": system_info["total_ram"],
            "mac_address": network["mac"],
            "enroll_key": self.config["enroll_key"]
        }

        r = requests.post(self.config["register_url"], json=payload)
        if r.status_code != 200:
            raise Exception(f"HTTP {r.status_code}")

        return r.json()

    @retry(5, 1)
    def send_telemetry(self, token, device_id):
        telemetry = self.telemetry.get()

        payload = {
            "device_id": device_id,
            "cpu_usage": telemetry["cpu_usage"],
            "ram_usage": telemetry["ram_usage"],
            "ip_local": telemetry["ip_local"],
            "ip_public": telemetry["ip_public"],
            "geo_country": telemetry["geo_country"],
            "geo_city": telemetry["geo_city"],
            "processes": telemetry["processes"],
            "disk_free": telemetry["disk_free"],
            "disk_total": telemetry["disk_total"],
            "network_sent": telemetry["network_sent"],
            "network_received": telemetry["network_received"],
            "active_connections": telemetry["active_connections"]
        }

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(self.config["update_url"], json=payload, headers=headers)

        Logger.info(f"Telemetry: {r.status_code} | CPU: {telemetry['cpu_usage']}% | RAM: {telemetry['ram_usage']}MB")

    @retry(5, 1)
    def send_heartbeat(self, device_id):
        payload = {
            "device_id": device_id
        }

        r = requests.post(self.config["heartbeat_url"], json=payload)

        Logger.info(f"Heartbeat: {r.status_code}")

    def start(self):
        Logger.info("Starting Python agent...")

        token, device_id = self.token_service.load()

        if not token:
            Logger.info("Registering device...")
            device = self.register()
            token = device["device_token"]
            device_id = device["device_id"]
            self.token_service.save(token, device_id)
            Logger.info("Device registered.")

        while True:
            self.send_telemetry(token, device_id)
            self.send_heartbeat(device_id)
            time.sleep(self.config["heartbeat_interval"])

if __name__ == "__main__":
    Agent().start()