import fastf1
from datetime import datetime
from fastf1.ergast import Ergast


def get_drivers_standings():
    ergast = Ergast()

    SEASON, ROUND = get_last_event_resume()

    standings = ergast.get_driver_standings(season=SEASON, round=ROUND)
    return standings.content[0]


def get_last_event_resume():
    current_year = datetime.now().year

    schedule = fastf1.get_event_schedule(current_year, include_testing=False)
    if schedule.empty:
        return
    
    past_events = schedule[schedule['EventDate'] < datetime.now()]
    last_event = past_events.iloc[-1]

    round = int(last_event['RoundNumber'])

    return current_year, round


def calculate_max_points_for_remaining_season():
    SEASON, ROUND = get_last_event_resume()

    POINTS_FOR_SPRINT = 8 + 25 # Winning the sprint and race
    POINTS_FOR_CONVENTIONAL = 25 # Winning the race

    events = fastf1.events.get_event_schedule(SEASON, backend='ergast')
    events = events[events['RoundNumber'] > ROUND]
    # Count how many sprints and conventional races are left
    sprint_events = len(events.loc[events["EventFormat"] == "sprint_shootout"])
    conventional_events = len(events.loc[events["EventFormat"] == "conventional"])

    # Calculate points for each
    sprint_points = sprint_events * POINTS_FOR_SPRINT
    conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL

    return sprint_points + conventional_points


def calculate(driver_standings, max_points, driver_code):
    full_message = []

    full_message.append(f"🏁 Chances de {driver_code} vencer o campeonato mundial:\n")

    driver_found = False

    LEADER_POINTS = int(driver_standings.loc[0]['points'])

    for i, _ in enumerate(driver_standings.iterrows()):
        driver = driver_standings.loc[i]

        if driver['driverCode'] == driver_code:
            driver_max_points = int(driver["points"]) + max_points
            can_win = 'Não' if driver_max_points < LEADER_POINTS else 'Sim'

            driver_found = True

            full_message.append(f"*{driver['position']}º - {driver['givenName'] + ' ' + driver['familyName']}*\n"
                f"Pontos atuais: {driver['points']}\n"
                f"Máximo de pontos: {driver_max_points}\n"
                f"Tem chance: {can_win}")

            break
    
    if not driver_found:
        full_message = []
        full_message.append(f"❌ Piloto {driver_code} não encontrado!")
    
    return '\n'.join(full_message)
        

def driver_chances_of_winning(driver_code):
    driver_standings = get_drivers_standings()
    points = calculate_max_points_for_remaining_season()

    return calculate(driver_standings, points, driver_code)
