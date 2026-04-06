from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.connection import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True)

    cpu_usage = Column(Float)
    ram_usage = Column(Float)

    ip_local = Column(String)
    ip_public = Column(String)

    geo_country = Column(String, nullable=True)
    geo_city = Column(String, nullable=True)

    processes = Column(String, nullable=True)  # JSON string

    disk_free = Column(Integer, nullable=True)
    disk_total = Column(Integer, nullable=True)
    network_sent = Column(Integer, nullable=True)
    network_received = Column(Integer, nullable=True)
    active_connections = Column(Integer, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device")