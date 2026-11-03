import fastf1
import matplotlib.pyplot as plt
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def avgGridLapTime(driver):
    laps = session.laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()
    return laps["LapTime"].mean().total_seconds()

def formatLapTime(seconds):
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"

@router.get("/average-lap")
@lru_cache(maxsize=64)
def averageLapAPI(year: int, race: str):
    global session
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    data = []
    for driver in session.results["Abbreviation"].tolist():
        try:
            average = avgGridLapTime(driver)
            data.append({
                "Driver": driver,
                "AverageLap": formatLapTime(average),
                "AverageLapSeconds": round(average, 3)
            })
        except Exception:
            continue

    data.sort(key=lambda x: x["AverageLapSeconds"])
    return data

if __name__ == "__main__":
    session = fastf1.get_session(2025, "Interlagos", "R")
    session.load()

    drivers = session.results["Abbreviation"].tolist()
    average_lap_times = [avgGridLapTime(driver) for driver in drivers]

    data = sorted(zip(drivers, average_lap_times), key=lambda x: x[1])
    drivers, average_lap_times = zip(*data)

    fig, ax = plt.subplots(figsize=(24, 8))
    fig.patch.set_facecolor("#15151E")
    ax.set_facecolor("#15151E")

    ax.plot(
        drivers, average_lap_times, color="#E10600", marker="o",
        markerfacecolor="#E10600", markeredgecolor="white",
        markersize=8, linewidth=2.5
    )

    for driver, average in zip(drivers, average_lap_times):
        ax.annotate(
            formatLapTime(average), (driver, average), xytext=(0, 10),
            textcoords="offset points", ha="center", color="white"
        )

    ax.set_title("Average Lap Time by Finishing Order", color="white", fontsize=18)
    ax.set_xlabel("Driver", color="white")
    ax.set_ylabel("Average Lap Time", color="white")
    ax.tick_params(axis="both", colors="white")
    ax.grid(axis="y", color="white", alpha=0.2)

    for spine in ax.spines.values():
        spine.set_color("#E10600")

    plt.tight_layout()
    plt.show()
