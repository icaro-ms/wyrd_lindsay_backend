from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

from app.models import Alert, LogEntry, Command
from app.services import (
    create_initial_history,
    update_alert_and_create_history,
    handle_alert_action,
    set_snooze_and_create_history
)
from app.db import get_alert_by_id, get_logs_by_alert_id

class SnoozeUpdate(BaseModel):
    snooze: Optional[int]  # null = remove soneca

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API para gerenciamento de alertas"}

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {
        "_id": alert["_id"],
        "id": alert["_id"],
        "status": alert["status"],
        "description": alert["description"],
        "responsible": alert["responsible"],
        "timestamp": alert["timestamp"],
        "snooze_time": alert.get("snooze_time", None),
        "notifications": alert.get("notifications", {}),
        "history": get_logs_by_alert_id(alert_id)
    }

@app.get("/alerts/{alert_id}/history")
async def get_alert_history(alert_id: str):
    logs = get_logs_by_alert_id(alert_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    return logs

@app.put("/alerts/{alert_id}")
async def update_alert(alert_id: str, alert_update: Alert):
    if not (alert_update.status and alert_update.description and alert_update.responsible):
        raise HTTPException(status_code=422, detail="status, description e responsible são obrigatórios")
    updated = update_alert_and_create_history(
        alert_id,
        alert_update.status,
        alert_update.description,
        alert_update.responsible,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"message": "Alerta atualizado com sucesso!"}

@app.post("/alerts/{alert_id}/{action}")
async def perform_action(alert_id: str, action: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    result = handle_alert_action(alert_id, action)
    if not result:
        raise HTTPException(status_code=400, detail=f"Erro ao executar ação: {action}")
    return {"message": f"Ação '{action}' executada com sucesso!"}

@app.post("/alerts/snooze/{alert_id}")
async def set_snooze(alert_id: str, payload: SnoozeUpdate):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    success = set_snooze_and_create_history(alert_id, payload.snooze)
    if not success:
        raise HTTPException(status_code=400, detail="Não foi possível atualizar a soneca")
    if payload.snooze is None:
        return {"message": "Soneca removida"}
    return {"message": f"Soneca definida para {payload.snooze} minutos"}
