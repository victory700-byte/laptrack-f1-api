import fastf1
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatTime(seconds):
    return f"{seconds:.3f}"

def displaySectorTimes(driver):
    driver = driver.upper()
    driver_laps = session.laps.pick_drivers(driver).pick_wo_box()
    columns = ["LapNumber", "Sector1Time", "Sector2Time", "Sector3Time"]
    sector_times = driver_laps[columns].dropna().copy()

    if sector_times.empty:
        print(f"No complete sector times found for {driver}.")
        return

    sector_times["LapNumber"] = sector_times["LapNumber"].astype(int)

    for column in columns[1:]:
        sector_times[column] = sector_times[column].apply(
            lambda time: formatTime(time.total_seconds())
        )

    print(f"\nSector times for {driver}:")
    print(sector_times.to_string(index=False))

@router.get("/sector-times")
@lru_cache(maxsize=128)
def sectorTimesAPI(year: int, race: str, driver: str):
    session_api = fastf1.get_session(year, race, "R")
    session_api.load(telemetry=False, weather=False, messages=False)

    driver = driver.upper()
    laps = session_api.laps.pick_drivers(driver).pick_wo_box()
    columns = ["LapNumber", "Sector1Time", "Sector2Time", "Sector3Time"]
    sector_times = laps[columns].dropna().copy()

    results = []
    for _, lap in sector_times.iterrows():
        results.append({
            "LapNumber": int(lap["LapNumber"]),
            "Sector1": formatTime(lap["Sector1Time"].total_seconds()),
            "Sector2": formatTime(lap["Sector2Time"].total_seconds()),
            "Sector3": formatTime(lap["Sector3Time"].total_seconds())
        })

    return {"Driver": driver, "Laps": results}

if __name__ == "__main__":
    session = fastf1.get_session(2026, "Monaco", "R")
    session.load()
    displaySectorTimes("VER")
