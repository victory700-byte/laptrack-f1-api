import fastf1
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()

def formatTime(seconds, pos=None):
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"

def tyreDegradation(year, race, driver1, driver2, stint):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#15151E")
    ax.set_facecolor("#15151E")
    all_laps = []

    for driver, color in zip([driver1, driver2], ["#E10600", "white"]):
        laps = session.laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()
        laps = laps[laps["Stint"] == stint].dropna(subset=["LapTime"])

        if laps.empty:
            continue

        x = laps["LapNumber"].astype(int)
        y = laps["LapTime"].dt.total_seconds()
        all_laps += x.tolist()

        ax.plot(
            x, y, "o-", color=color, linewidth=2,
            label=f"{driver} — {laps['Compound'].iloc[0]}"
        )

    if not all_laps:
        return fig

    for lap in range(min(all_laps), max(all_laps) + 1):
        status = session.laps[
            session.laps["LapNumber"] == lap
        ]["TrackStatus"].astype(str)

        if status.str.contains("4").any():
            ax.axvspan(lap - .5, lap + .5, color="yellow", alpha=.12)

    ax.set(
        title=f"Tyre Degradation — Stint {stint}",
        xlabel="Race Lap",
        ylabel="Lap Time"
    )

    ax.set_xticks(range(min(all_laps), max(all_laps) + 1))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatTime))
    ax.tick_params(colors="white")
    ax.title.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.grid(axis="y", alpha=.15)
    ax.legend(frameon=False, labelcolor="white")

    plt.tight_layout()
    return fig

@router.get("/tyre-degradation")
@lru_cache(maxsize=128)
def tyreDegradationAPI(year: int, race: str, driver1: str, driver2: str, stint: int):
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)

    results = {}

    for driver in [driver1.upper(), driver2.upper()]:
        laps = session.laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()
        laps = laps[laps["Stint"] == stint].dropna(subset=["LapTime"])

        if laps.empty:
            results[driver] = {"Compound": None, "Laps": []}
            continue

        lap_data = []

        for _, lap in laps.iterrows():
            seconds = lap["LapTime"].total_seconds()

            lap_data.append({
                "Lap": int(lap["LapNumber"]),
                "Time": formatTime(seconds),
                "TimeSeconds": round(seconds, 3),
                "SafetyCar": "4" in str(lap["TrackStatus"])
            })

        results[driver] = {
            "Compound": laps["Compound"].iloc[0],
            "Laps": lap_data
        }

    return {"Race": race, "Stint": stint, "Drivers": results}

if __name__ == "__main__":
    tyreDegradation(2025, "Qatar", "NOR", "PIA", 1)
    plt.show()
