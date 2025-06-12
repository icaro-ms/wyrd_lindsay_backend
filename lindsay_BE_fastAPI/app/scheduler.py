from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from twilio.rest import Client
from app.db import get_alerts_due_for_snooze, update_alert_field, save_log_to_db
from app.models import LogEntry
import os

# inicializa Twilio
twilio = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TO   = os.getenv("WHATSAPP_TO")

def job_check_snoozes():
    now_iso = datetime.utcnow().isoformat()
    # 1) pega todos os alertas vencidos
    alerts = get_alerts_due_for_snooze(now_iso)
    for alert in alerts:
        # 2) envia WhatsApp
        body = (
            f"🔔 ALERTA #{alert['_id']} DESPERTANDO 🔔\n"
            f"{alert['description']}\n"
            f"Responsável: {alert.get('responsible','-')}"
        )
        try:
            twilio.messages.create(body=body, from_=FROM, to=TO)
        except Exception as e:
            print("Erro enviando WhatsApp:", e)
            continue

        # 3) registra no histórico
        log = LogEntry(
            alert_id=alert["_id"],
            action="whatsapp_sent_after_snooze",
            responsible="system",
            timestamp=datetime.utcnow(),
            type="log"
        )
        save_log_to_db(log.dict())

        # 4) limpa soneca
        update_alert_field(alert["_id"], {"snooze_time": None, "snooze_until": None})

# configura o scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(job_check_snoozes, "interval", minutes=1, next_run_time=datetime.utcnow())
scheduler.start()
