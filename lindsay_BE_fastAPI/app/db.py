import couchdb
from app.models import Alert

COUCHDB_URL = "https://admin:wyrd@db.vpn.ind.br"
DATABASE_NAME = "mqtt_data"

server = couchdb.Server(COUCHDB_URL)
try:
    db = server[DATABASE_NAME]
except couchdb.http.ResourceNotFound:
    db = server.create(DATABASE_NAME)

def get_alerts_from_db():
    return [doc for doc in db.view('_all_docs', include_docs=True)]

def save_alert_to_db(alert: Alert):
    db[alert.id] = alert.dict()

def get_alert_by_id(alert_id: str):
    return db.get(alert_id)
