# __init__.py para inicializar o pacote 'app'

from .models import Alert, LogEntry
from .db import get_alert_by_id, save_alert_to_db, save_log_to_db, get_logs_by_alert_id
from .services import create_initial_history, update_alert_and_create_history