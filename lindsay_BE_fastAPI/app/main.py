from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models import Alert, LogEntry
from app.db import get_alert_by_id, save_alert_to_db, save_log_to_db
from app.services import handle_alert_action

app = FastAPI() 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# fuso de Brasília
BR_TZ = ZoneInfo("America/Sao_Paulo")

@app.get("/")
def read_root():
    return {"message": "API para gerenciamento de alertas"}

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return alert

@app.get("/alerts/history/{alert_id}")
async def get_alert_history(alert_id: str):
    from app.db import get_logs_by_alert_id
    logs = get_logs_by_alert_id(alert_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    return logs

@app.post("/alerts/{action}/{alert_id}")
async def perform_action(alert_id: str, action: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    result = handle_alert_action(alert_id, action)
    if not result:
        raise HTTPException(status_code=400, detail=f"Erro ao executar ação: {action}")
    return {"message": f"Ação '{action}' executada com sucesso!"}

@app.put("/alerts/update/{alert_id}")
async def update_alert(alert_id: str, payload: Alert):
    existing = get_alert_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    now = datetime.now(BR_TZ)

    # 1) Atualiza campos de descrição, responsável e notificações
    for field in ("description", "responsible", "notifications"):
        new = getattr(payload, field)
        old = existing.get(field)
        if new is not None and new != old:
            existing[field] = new
            log = LogEntry(
                alert_id=alert_id,
                action=f"{field} alterado para {new}",
                responsible=payload.responsible or "",
                timestamp=now,
                type="log"
            )
            save_log_to_db(log.dict())

    # 2) Trata o campo snooze_time e recalcula snooze_until
    new_snooze = payload.snooze_time
    old_snooze = existing.get("snooze_time")
    if new_snooze != old_snooze:
        existing["snooze_time"] = new_snooze
        if new_snooze is not None:
            existing["snooze_until"] = (now + timedelta(minutes=new_snooze)).isoformat()
            action = f"lembrete para {new_snooze} min"
        else:
            existing["snooze_until"] = None
            action = "lembrete removido"

        log = LogEntry(
            alert_id=alert_id,
            action=action,
            responsible=payload.responsible or "",
            timestamp=now,
            type="log"
        )
        save_log_to_db(log.dict())

    # 3) Atualiza timestamp geral
    existing["timestamp"] = now.isoformat()

    # 4) Persiste no CouchDB
    saved = save_alert_to_db(existing)
    if not saved:
        raise HTTPException(status_code=500, detail="Erro ao salvar alerta no BD")

    return {"message": "Alerta atualizado com sucesso!"}
