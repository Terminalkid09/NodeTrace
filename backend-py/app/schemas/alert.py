from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    alert_type: str
    severity: str
    message: str
    alert_value: Optional[float]
    resolved: bool
    resolved_at: Optional[datetime]
    timestamp: datetime