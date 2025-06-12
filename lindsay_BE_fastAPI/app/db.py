import requests
from datetime import datetime
from typing import Optional

COUCHDB_URL = "https://admin:wyrd@db.vpn.ind.br"
DATABASE_NAME = "mqtt_data"

def convert_datetime_fields(data: dict) -> dict:
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

def get_alert_by_id(alert_id: str) -> Optional[dict]:
    resp = requests.get(f"{COUCHDB_URL}/{DATABASE_NAME}/{alert_id}")
    if resp.status_code == 200:
        return resp.json()
    return None

def save_alert_to_db(alert: dict) -> Optional[str]:
    if not isinstance(alert, dict): return None
    for f in ["status", "description", "responsible"]:
        if f not in alert: return None
    alert = convert_datetime_fields(alert)
    resp = requests.post(f"{COUCHDB_URL}/{DATABASE_NAME}", json=alert)
    if resp.status_code == 201:
        return resp.json().get("id")
    return None

def update_alert_in_db(alert: dict) -> Optional[str]:
    alert_id = alert.get("_id")
    alert_rev = alert.get("_rev")
    if alert_id and alert_rev:
        alert = convert_datetime_fields(alert)
        resp = requests.put(f"{COUCHDB_URL}/{DATABASE_NAME}/{alert_id}", json=alert)
        if resp.status_code == 200:
            return resp.json().get("id")
    return None

def update_alert_field(alert_id: str, fields: dict) -> bool:
    alert = get_alert_by_id(alert_id)
    if not alert:
        return False
    alert.update(fields)
    return update_alert_in_db(alert) is not None

def save_log_to_db(log_entry: dict) -> bool:
    log_entry = convert_datetime_fields(log_entry)
    resp = requests.post(f"{COUCHDB_URL}/{DATABASE_NAME}", json=log_entry)
    return resp.status_code == 201

def get_logs_by_alert_id(alert_id: str):
    resp = requests.get(
        f"{COUCHDB_URL}/{DATABASE_NAME}/_design/logs/_view/by_alert_id?key=\"{alert_id}\""
    )
    if resp.status_code == 200:
        return [r["value"] for r in resp.json().get("rows", [])]
    return []

def save_command_to_db(command_data: dict):
    command_data = convert_datetime_fields(command_data)
    requests.post(f"{COUCHDB_URL}/{DATABASE_NAME}", json=command_data)
