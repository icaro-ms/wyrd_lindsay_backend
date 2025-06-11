from pydantic import BaseModel
from typing import Optional, Dict

class Alert(BaseModel):
    id: str
    description: str
    status: str
    timestamp: int
    notifications: Optional[Dict[str, bool]] = None

    class Config:
        orm_mode = True
