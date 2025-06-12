from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Alert(BaseModel):
    status: str
    description: str
    responsible: str
    timestamp: Optional[datetime] = None
    class Config:
        json_encoders = { datetime: lambda v: v.isoformat() }

class LogEntry(BaseModel):
    alert_id: str
    action: str
    responsible: str
    timestamp: datetime
    type: str
    class Config:
        json_encoders = { datetime: lambda v: v.isoformat() }

class Command(BaseModel):
    topic: str
    payload: str
    origin: str
    timestamp: str
    qos: int
