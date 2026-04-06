from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertOut(BaseModel):
    id: int
    device_id: str
    alert_type: str
    severity: str
    message: str
    alert_value: Optional[float]
    resolved: bool
    resolved_at: Optional[datetime]
    timestamp: datetime

    class Config:
        from_attributes = True