from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TelemetryData(BaseModel):
    device_id: str
    cpu_usage: float
    ram_usage: float
    ip_local: str
    ip_public: str
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    processes: Optional[List[str]] = None
    disk_free: Optional[int] = None  # MB
    disk_total: Optional[int] = None  # MB
    network_sent: Optional[int] = None  # bytes
    network_received: Optional[int] = None  # bytes
    active_connections: Optional[int] = None

class Heartbeat(BaseModel):
    device_id: str

class DeviceOut(BaseModel):
    device_id: str
    hostname: str
    os: str
    os_version: str
    cpu_model: str
    total_ram: int
    mac_address: str
    last_seen: datetime
    status: str # on o off

    class Config:
        orm_mode = True # per leggere direttamente gli oggetti sqlalchemy

class TelemetryOut(BaseModel):
    timestamp: datetime
    cpu_usage: float
    ram_usage: float
    ip_local: str
    ip_public: str
    geo_country: Optional[str]
    geo_city: Optional[str]
    processes: Optional[List[str]]
    disk_free: Optional[int]
    disk_total: Optional[int]
    network_sent: Optional[int]
    network_received: Optional[int]
    active_connections: Optional[int]

    class Config:
        orm_mode = True

class DeviceDetail(BaseModel):
    device_id: str
    hostname: str
    os: str
    os_version: str
    cpu_model: str
    total_ram: int
    mac_address: str
    last_seen: datetime
    status: str
    latest_telemetry: Optional[TelemetryOut]
    telemetry_history: Optional[List[TelemetryOut]]
    active_alerts_count: int

    class Config:
        orm_mode = True

class StatusOut(BaseModel):
    total: int
    online: int
    offline: int
    timestamp: datetime

class DeviceRegister(BaseModel):
    hostname: str
    os: str
    os_version: str
    cpu_model: str
    total_ram: int
    mac_address: str
    enroll_key: str
