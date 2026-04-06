from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.connection import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)  # Not foreign key for simplicity, but could be

    alert_type = Column(String)  # e.g., "cpu_high", "disk_low"
    severity = Column(String)  # "warning", "critical"
    message = Column(String)
    alert_value = Column(Float, nullable=True)  # The value that triggered the alert
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)