from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from zoneinfo import ZoneInfo

# Fuso de Brasília
BR_TZ = ZoneInfo("America/Sao_Paulo")

class Alert(BaseModel):
    status: str
    description: str
    responsible: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(BR_TZ))
    snooze_time: Optional[int] = None       # duração da soneca em minutos
    snooze_until: Optional[datetime] = None # quando a soneca termina (timezone-aware)
    notifications: Dict[str, bool] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True


class LogEntry(BaseModel):
    alert_id: str
    action: str
    responsible: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(BR_TZ))
    type: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Command(BaseModel):
    topic: str
    payload: str
    origin: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(BR_TZ))
    qos: int

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
