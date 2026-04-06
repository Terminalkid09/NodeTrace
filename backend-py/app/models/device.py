from sqlalchemy import Column, String, Integer
from app.database.connection import Base
from datetime import datetime
from sqlalchemy import DateTime

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    hostname = Column(String, index=True)
    os = Column(String)
    os_version = Column(String)
    cpu_model = Column(String)
    total_ram = Column(Integer)  # in MB
    mac_address = Column(String, unique=True, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    device_token = Column(String, unique=True, index=True)