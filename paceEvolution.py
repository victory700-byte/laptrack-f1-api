import fastf1
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatGap(seconds):
    return f"+{int(seconds // 60)}:{seconds % 60:06.3f}" if seconds >= 60 else f"+{seconds:.3f}"

def driverPace(session, driver):
    laps = session.laps.pick_drivers(driver).pick_quicklaps()
    if session.name == "Race":
        laps = laps.pick_wo_box()
    return laps["LapTime"].dt.total_seconds().mean()

def paceEvolution(year, races, driver, session_type="R"):
    data = []

    for race in races:
        try:
            session = fastf1.get_session(year, race, session_type)
            session.load(telemetry=False, weather=False, messages=False)

            pace = {
                d: driverPace(session, d)
                for d in session.laps["Driver"].dropna().unique()
            }
            pace = {d: p for d, p in pace.items() if p == p}

            if driver in pace:
                delta = pace[driver] - min(pace.values())
                data.append({
                    "Race": race,
                    "Delta": formatGap(delta),
                    "DeltaSeconds": round(delta, 3)
                })
        except Exception:
            continue

    return data

def paceTrend(data):
    if len(data) < 2:
        return "Not enough data"

    start = data[0]["DeltaSeconds"]
    end = data[-1]["DeltaSeconds"]

    if end < start:
        return "Improving"
    if end > start:
        return "Declining"
    return "Stable"

@router.get("/pace-evolution")
@lru_cache(maxsize=64)
def paceEvolutionAPI(year: int, driver: str, session_type: str = "R"):
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    races = schedule["EventName"].dropna().tolist()
    data = paceEvolution(year, races, driver.upper(), session_type.upper())

    return {
        "Driver": driver.upper(),
        "Session": session_type.upper(),
        "Trend": paceTrend(data),
        "Races": data
    }

if __name__ == "__main__":
    races = [
        "Australia", "China", "Japan", "Bahrain", "Saudi Arabia", "Miami",
        "Emilia Romagna", "Monaco", "Spain", "Canada", "Austria", "Great Britain"
    ]

    data = paceEvolution(2025, races, "NOR", "R")
    print(data)
    print("Trend:", paceTrend(data))
