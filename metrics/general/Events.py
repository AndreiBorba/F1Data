import fastf1
from utils.sys import Time
from datetime import datetime, timedelta
import pytz


def get_remaining_events():
    full_message = []

    full_message.append("📅 Próximas corridas:")

    data_ergast = fastf1.get_events_remaining(dt=datetime.now(), include_testing=False, backend='ergast')
    if not data_ergast.empty:
        print(f"usando data_ergast\n")
        return format_events(full_message, data_ergast)

    return


def format_events(full_message, data):
    sp_tz = pytz.timezone('America/Sao_Paulo')

    for index, row in data[['EventName', 'EventDate']].iterrows():
        event_date = row['EventDate']

        if event_date.tzinfo is None:
            event_date = pytz.utc.localize(event_date)
        
        event_date_sp = event_date.astimezone(sp_tz)
        formatted_date = event_date_sp.strftime('%d/%m/%Y - %H:%M')
        
        full_message.append(f"\n📍 {row['EventName']}\n🕑 {formatted_date}")
    
    return '\n'.join(full_message)
