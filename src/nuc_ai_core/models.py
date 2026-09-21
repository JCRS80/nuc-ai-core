from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TelemetryEvent(SQLModel, table=True):
    __tablename__ = "telemetry_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True)
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
