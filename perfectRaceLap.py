import fastf1
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatLapTime(time):
    seconds = time.total_seconds()
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"

def formatSectorTime(time):
    return f"{time.total_seconds():.3f}"

def formatGap(seconds):
    return f"+{int(seconds // 60)}:{seconds % 60:06.3f}" if seconds >= 60 else f"+{seconds:.3f}"

def wasWetRace(session):
    compounds = session.laps["Compound"].dropna().unique()
    return "INTERMEDIATE" in compounds or "WET" in compounds

def perfectRaceLap(year, race):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps.copy()
    wet_race = wasWetRace(session)

    s1 = laps.dropna(subset=["Sector1Time"])
    s2 = laps.dropna(subset=["Sector2Time"])
    s3 = laps.dropna(subset=["Sector3Time"])

    sector1_row = s1.loc[s1["Sector1Time"].idxmin()]
    sector2_row = s2.loc[s2["Sector2Time"].idxmin()]
    sector3_row = s3.loc[s3["Sector3Time"].idxmin()]

    perfect_lap = (
        sector1_row["Sector1Time"]
        + sector2_row["Sector2Time"]
        + sector3_row["Sector3Time"]
    )

    fastest_race_lap = session.laps.pick_fastest()
    fastest_race_time = fastest_race_lap["LapTime"]
    difference = fastest_race_time - perfect_lap

    print(f"\n{year} {race} Grand Prix")
    print("=" * 45)
    print(f"Wet Race: {'Yes' if wet_race else 'No'}")
    print(f"\nActual Fastest Race Lap: {formatLapTime(fastest_race_time)} — {fastest_race_lap['Driver']}")
    print(f"\nSector 1: {formatSectorTime(sector1_row['Sector1Time'])} — {sector1_row['Driver']}")
    print(f"Sector 2: {formatSectorTime(sector2_row['Sector2Time'])} — {sector2_row['Driver']}")
    print(f"Sector 3: {formatSectorTime(sector3_row['Sector3Time'])} — {sector3_row['Driver']}")
    print(f"\nPerfect Race Lap: {formatLapTime(perfect_lap)}")
    print(f"\nTheoretical Improvement: {formatGap(difference.total_seconds())}")

@router.get("/perfect-race-lap")
@lru_cache(maxsize=64)
def perfectRaceLapAPI(year: int, race: str):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps.copy()
    s1 = laps.dropna(subset=["Sector1Time"])
    s2 = laps.dropna(subset=["Sector2Time"])
    s3 = laps.dropna(subset=["Sector3Time"])

    sector1_row = s1.loc[s1["Sector1Time"].idxmin()]
    sector2_row = s2.loc[s2["Sector2Time"].idxmin()]
    sector3_row = s3.loc[s3["Sector3Time"].idxmin()]

    perfect_lap = (
        sector1_row["Sector1Time"]
        + sector2_row["Sector2Time"]
        + sector3_row["Sector3Time"]
    )

    fastest = session.laps.pick_fastest()
    fastest_time = fastest["LapTime"]
    gap = (fastest_time - perfect_lap).total_seconds()

    return {
        "WetRace": wasWetRace(session),
        "Sector1": {
            "Driver": sector1_row["Driver"],
            "Time": formatSectorTime(sector1_row["Sector1Time"])
        },
        "Sector2": {
            "Driver": sector2_row["Driver"],
            "Time": formatSectorTime(sector2_row["Sector2Time"])
        },
        "Sector3": {
            "Driver": sector3_row["Driver"],
            "Time": formatSectorTime(sector3_row["Sector3Time"])
        },
        "PerfectLap": formatLapTime(perfect_lap),
        "PerfectLapSeconds": round(perfect_lap.total_seconds(), 3),
        "FastestActualLap": {
            "Driver": fastest["Driver"],
            "Time": formatLapTime(fastest_time),
            "TimeSeconds": round(fastest_time.total_seconds(), 3)
        },
        "TheoreticalImprovement": formatGap(gap)
    }

if __name__ == "__main__":
    perfectRaceLap(2024, "Netherlands")
