from datetime import datetime, timedelta
from app.db import get_alert_by_id, save_alert_to_db
import time

def set_alarm_snooze(alert_id: str, snooze_time: int):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise ValueError(f"Alerta {alert_id} não encontrado.")
    
    alert.status = "Em progresso"
    alert.timestamp = time.time() + snooze_time * 60  # Novo timestamp para reativação

    save_alert_to_db(alert)  # Salva o alerta atualizado
    return alert

def update_alert_description(alert_id: str, description: str, notifications: dict):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise ValueError(f"Alerta {alert_id} não encontrado.")
    
    alert.description = description
    alert.notifications = notifications
    
    save_alert_to_db(alert)
    return alert
