import fastf1
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatSectorTime(time):
    return f"{time.total_seconds():.3f}"

def formatGap(seconds):
    return f"+{int(seconds // 60)}:{seconds % 60:06.3f}" if seconds >= 60 else f"+{seconds:.3f}"

def wasWetRace(session):
    compounds = session.laps["Compound"].dropna().unique()
    return "INTERMEDIATE" in compounds or "WET" in compounds

def getFastestSectors(session, driver):
    laps = session.laps.pick_drivers(driver)
    return {
        "Sector1": laps["Sector1Time"].min(),
        "Sector2": laps["Sector2Time"].min(),
        "Sector3": laps["Sector3Time"].min()
    }

def compareDrivers(year, race, driver1, driver2):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    wet_race = wasWetRace(session)
    driver1_sectors = getFastestSectors(session, driver1)
    driver2_sectors = getFastestSectors(session, driver2)
    driver1_score = driver2_score = 0

    print(f"\n{year} {race} Grand Prix")
    print(f"{driver1} vs {driver2}")
    print("=" * 45)
    print(f"Wet Race: {'Yes' if wet_race else 'No'}")

    for sector in ["Sector1", "Sector2", "Sector3"]:
        time1 = driver1_sectors[sector]
        time2 = driver2_sectors[sector]
        gap = abs(time1.total_seconds() - time2.total_seconds())

        print(f"\n{sector}")
        print(f"{driver1}: {formatSectorTime(time1)}")
        print(f"{driver2}: {formatSectorTime(time2)}")

        if time1 < time2:
            driver1_score += 1
            print(f"{driver1} faster by {formatGap(gap)}")
        elif time2 < time1:
            driver2_score += 1
            print(f"{driver2} faster by {formatGap(gap)}")
        else:
            print("Equal sector time")

    print("\nOVERALL SECTOR COMPARISON")
    print(f"{driver1}: {driver1_score} sectors won")
    print(f"{driver2}: {driver2_score} sectors won")

@router.get("/sector-comparison")
@lru_cache(maxsize=128)
def sectorComparisonAPI(year: int, race: str, driver1: str, driver2: str):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    driver1, driver2 = driver1.upper(), driver2.upper()
    sectors1 = getFastestSectors(session, driver1)
    sectors2 = getFastestSectors(session, driver2)

    results = {}
    score1 = score2 = 0

    for sector in ["Sector1", "Sector2", "Sector3"]:
        raw1 = sectors1[sector].total_seconds()
        raw2 = sectors2[sector].total_seconds()

        if raw1 < raw2:
            winner = driver1
            score1 += 1
        elif raw2 < raw1:
            winner = driver2
            score2 += 1
        else:
            winner = "Tie"

        results[sector] = {
            driver1: f"{raw1:.3f}",
            driver2: f"{raw2:.3f}",
            "Gap": formatGap(abs(raw1 - raw2)),
            "Winner": winner
        }

    return {
        "Driver1": driver1,
        "Driver2": driver2,
        "WetRace": wasWetRace(session),
        "Sectors": results,
        "Score": {driver1: score1, driver2: score2}
    }

if __name__ == "__main__":
    compareDrivers(2023, "Monaco", "VER", "ALO")
