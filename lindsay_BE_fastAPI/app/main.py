from fastapi import FastAPI, HTTPException
from app.models import Alert
from app.services import set_alarm_snooze, update_alert_description
from app.db import get_alerts_from_db
from pydantic import BaseModel

app = FastAPI()

@app.get("/alerts")
async def get_alerts():
    alerts = get_alerts_from_db()
    return alerts

class SnoozeRequest(BaseModel):
    snoozeTime: int

@app.post("/snooze")
async def snooze_alert(alert_id: str, snooze_request: SnoozeRequest):
    try:
        alert = set_alarm_snooze(alert_id, snooze_request.snoozeTime)
        return {"message": f"Alarme {alert.id} colocado em soneca por {snooze_request.snoozeTime} minutos."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/alerts/{alert_id}")
async def update_alert(alert_id: str, alert: Alert):
    try:
        updated_alert = update_alert_description(alert_id, alert.description, alert.notifications)
        return updated_alert
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/alerts/{alert_id}/status")
async def update_alert_status(alert_id: str, status: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado.")
    alert.status = status
    save_alert_to_db(alert)
    return alert
