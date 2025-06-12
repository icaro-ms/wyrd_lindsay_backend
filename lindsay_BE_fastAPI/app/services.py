from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

from app.db import (
    get_alert_by_id,
    save_alert_to_db,
    save_log_to_db,
    save_command_to_db,
    update_alert_field
)
from app.models import LogEntry, Command

# Fuso de Brasília
BR_TZ = ZoneInfo("America/Sao_Paulo")

def create_initial_history(alert_id: str):
    now = datetime.now(BR_TZ)
    log_entry = LogEntry(
        alert_id=alert_id,
        action="Alerta gerado",
        responsible="",
        timestamp=now,
        type="log"
    )
    return save_log_to_db(log_entry.dict())

def update_alert_and_create_history(alert_id: str, status: str, description: str, responsible: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        return None

    now = datetime.now(BR_TZ)
    alert["status"] = status
    alert["description"] = description
    alert["responsible"] = responsible
    alert["timestamp"] = now.isoformat()
    save_alert_to_db(alert)

    log_entry = LogEntry(
        alert_id=alert_id,
        action=f"Status alterado para {status}",
        responsible=responsible,
        timestamp=now,
        type="log"
    )
    save_log_to_db(log_entry.dict())
    return alert

def handle_alert_action(alert_id: str, action: str):
    alert = get_alert_by_id(alert_id)
    if not alert:
        return None

    if action == "toggle_alarm":
        new_status = "Alarmado" if alert["status"] != "Alarmado" else "Normal"
        update_alert_and_create_history(alert_id, new_status, alert["description"], alert["responsible"])
    elif action == "activate_siren":
        update_alert_and_create_history(alert_id, "Sirene Ativada", alert["description"], alert["responsible"])
    else:
        return None

    irrigador_id = alert.get("irrigadorId", "")
    topic = f"lindsay/comandos/{irrigador_id}"
    payload = f"{irrigador_id};{action}"
    command = Command(
        topic=topic,
        payload=payload,
        origin="app",
        timestamp=datetime.now(BR_TZ).isoformat(),
        qos=0
    )
    save_command_to_db(command.dict())
    return True

def set_snooze_and_create_history(alert_id: str, snooze: Optional[int]) -> bool:
    now = datetime.now(BR_TZ)
    # calcula quando a soneca termina
    fields = {"snooze_time": snooze}
    if snooze is not None:
        fields["snooze_until"] = (now + timedelta(minutes=snooze)).isoformat()
    else:
        fields["snooze_until"] = None

    updated = update_alert_field(alert_id, fields)
    if not updated:
        return False

    action = "clear_snooze" if snooze is None else f"set_snooze_{snooze}m"
    log_entry = LogEntry(
        alert_id=alert_id,
        action=action,
        responsible="",
        timestamp=now,
        type="log"
    )
    save_log_to_db(log_entry.dict())
    return True
