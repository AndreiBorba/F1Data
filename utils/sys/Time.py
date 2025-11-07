from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_now_br():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))
