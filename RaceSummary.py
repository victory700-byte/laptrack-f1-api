import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatLapTime(seconds):
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"

def formatTime(seconds):
    return f"{seconds:.3f}"

def formatGap(seconds):
    return f"+{formatLapTime(seconds)}" if seconds >= 60 else f"+{seconds:.3f}"

def formatConsistency(seconds):
    return f"±{seconds:.3f}"

def getRaceSummary(year, race):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    driver_data = []

    for _, result in session.results.iterrows():
        driver = result["Abbreviation"]
        laps = session.laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()

        if laps.empty:
            continue

        lap = laps["LapTime"].dt.total_seconds()
        s1 = laps["Sector1Time"].dt.total_seconds().min()
        s2 = laps["Sector2Time"].dt.total_seconds().min()
        s3 = laps["Sector3Time"].dt.total_seconds().min()
        perfect = s1 + s2 + s3

        driver_data.append({
            "Driver": driver,
            "Name": result["FullName"],
            "Team": result["TeamName"],
            "Finish": int(result["Position"]),
            "AverageLap": lap.mean(),
            "Consistency": lap.std(),
            "Sector1": s1,
            "Sector2": s2,
            "Sector3": s3,
            "PerfectLap": perfect,
            "FastestLap": lap.min(),
            "TimeLeft": lap.min() - perfect
        })

    data = pd.DataFrame(driver_data)
    data["PaceRank"] = data["AverageLap"].rank().astype(int)
    data["ConsistencyRank"] = data["Consistency"].rank().astype(int)
    return data

def getAwards(data):
    return {
        "Fastest Average Pace": data.loc[data["AverageLap"].idxmin(), "Driver"],
        "Most Consistent": data.loc[data["Consistency"].idxmin(), "Driver"],
        "Best Sector 1": data.loc[data["Sector1"].idxmin(), "Driver"],
        "Best Sector 2": data.loc[data["Sector2"].idxmin(), "Driver"],
        "Best Sector 3": data.loc[data["Sector3"].idxmin(), "Driver"],
        "Best Lap Execution": data.loc[data["TimeLeft"].idxmin(), "Driver"]
    }

def showRaceSummary(data, awards, race):
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#15151E")
    ax.set_facecolor("#15151E")
    ax.axis("off")

    ax.text(
        0.5, 0.95, f"{race.upper()} RACE SUMMARY",
        color="white", fontsize=22, weight="bold", ha="center"
    )

    y = 0.82
    for _, driver in data.sort_values("Finish").iterrows():
        ax.text(
            0.05, y, f"P{driver['Finish']}  {driver['Driver']}",
            color="#E10600", fontsize=13, weight="bold"
        )
        ax.text(
            0.20, y,
            f"Pace: P{driver['PaceRank']}    "
            f"Consistency: P{driver['ConsistencyRank']} {formatConsistency(driver['Consistency'])}",
            color="white", fontsize=11
        )
        y -= 0.035

    y -= 0.03
    ax.text(
        0.05, y, "PERFORMANCE AWARDS",
        color="#E10600", fontsize=16, weight="bold"
    )

    for award, driver in awards.items():
        y -= 0.045
        ax.text(0.05, y, award, color="white", fontsize=11)
        ax.text(0.40, y, driver, color="#E10600", fontsize=11, weight="bold")

    plt.tight_layout()
    return fig

@router.get("/race-summary")
@lru_cache(maxsize=64)
def raceSummaryAPI(year: int, race: str):
    summary = getRaceSummary(year, race)
    awards = getAwards(summary)
    drivers = []

    for _, d in summary.iterrows():
        drivers.append({
            "Driver": d["Driver"],
            "Name": d["Name"],
            "Team": d["Team"],
            "Finish": int(d["Finish"]),
            "AverageLap": formatLapTime(d["AverageLap"]),
            "AverageLapSeconds": round(float(d["AverageLap"]), 3),
            "Consistency": formatConsistency(d["Consistency"]),
            "ConsistencySeconds": round(float(d["Consistency"]), 3),
            "Sector1": formatTime(d["Sector1"]),
            "Sector2": formatTime(d["Sector2"]),
            "Sector3": formatTime(d["Sector3"]),
            "PerfectLap": formatLapTime(d["PerfectLap"]),
            "FastestLap": formatLapTime(d["FastestLap"]),
            "TimeLeft": formatGap(d["TimeLeft"]),
            "PaceRank": int(d["PaceRank"]),
            "ConsistencyRank": int(d["ConsistencyRank"])
        })

    return {"Race": race, "Drivers": drivers, "Awards": awards}

if __name__ == "__main__":
    race = "Qatar"
    summary = getRaceSummary(2025, race)
    awards = getAwards(summary)
    showRaceSummary(summary, awards, race)
    plt.show()
