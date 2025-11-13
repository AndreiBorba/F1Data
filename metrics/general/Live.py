import requests, logging
from datetime import datetime, timezone

from utils.openf1 import OpenF1Service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def top_5_live():
    full_message = []

    race_types = [
        'Practice 1',
        'Practice 2',
        'Practice 3',
        'Qualifying',
        'Sprint Qualifying',
        'Sprint',
        'Race'
    ]

    now = datetime.now(timezone.utc)
    current_year = datetime.now().year
    
    response = OpenF1Service.get_sessions_by_year(year=current_year)

    if response.status_code != 200:
        full_message.append(f"❌ Sem dados!")
        return full_message
    
    sessions = response.json()

    # Filtrando pelo tipo de corrida
    races = [s for s in sessions if s['session_name'] in race_types]
    
    # Encontrar corrida ao vivo ou mais recente
    current_race = None
    
    for race in sorted(races, key=lambda x: x['date_start'], reverse=True):
        date_start = datetime.fromisoformat(race['date_start'].replace('Z', '+00:00'))
        date_end = datetime.fromisoformat(race['date_end'].replace('Z', '+00:00'))
        
        # Se está acontecendo agora
        if date_start <= now <= date_end:
            current_race = race
            full_message.append(f"🔴 AO VIVO ({current_race.get('session_name', 'N/A')})")
            break
        
        # Se já passou, pegar a mais recente
        if now > date_end and current_race is None:
            current_race = race
            full_message.append(f"✅ Último evento ({current_race.get('session_name', 'N/A')})")
            break
    
    if not current_race:
        full_message.append("❌ Nenhuma corrida disponível")
        return
    
    session_key = current_race['session_key']
    
    # Mostrar informações disponíveis da corrida
    location = current_race.get('location', 'N/A')
    country = current_race.get('country_name', 'N/A')
    circuit = current_race.get('circuit_short_name', 'N/A')
    
    full_message.append(f"📍 {location}, {country}")
    full_message.append(f"🏟️ Circuito: {circuit}")
    full_message.append(f"📅 Data: {current_race.get('date_start', 'N/A')[:10]}\n")

    # Buscar posições
    positions = requests.get("https://api.openf1.org/v1/position",
                            params={'session_key': session_key}).json()
    
    if not positions:
        full_message.append("❌ Sem dados de posição")
        return
    
    # Buscar pilotos
    drivers = requests.get("https://api.openf1.org/v1/drivers",
                          params={'session_key': session_key}).json()
    
    driver_dict = {d['driver_number']: d for d in drivers}
    
    # Última posição de cada piloto
    latest_pos = {}
    for p in positions:
        num = p['driver_number']
        if num not in latest_pos or p['date'] > latest_pos[num]['date']:
            latest_pos[num] = p
    
    # Top 5
    top5 = sorted(latest_pos.values(), key=lambda x: x['position'])[:5]
    
    full_message.append("🏆 TOP 5 POSIÇÕES\n")
    for p in top5:
        driver = driver_dict.get(p['driver_number'], {})
        abbr = driver.get('name_acronym', '???')
        team = driver.get('team_name', 'N/A')
        
        full_message.append(f"{p['position']}º - {abbr} - {team}")
    
    return '\n'.join(full_message)
