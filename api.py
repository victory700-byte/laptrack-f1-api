import os
from pathlib import Path

import fastf1
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastf1.exceptions import DataNotLoadedError

from RaceSummary import router as race_summary_router
from averageLapTime import router as average_lap_router
from sectorTimes import router as sector_times_router
from driverbydriverSectorTimes import router as sector_comparison_router
from perfectRaceLap import router as perfect_lap_router
from paceEvolution import router as pace_evolution_router
from tyreDeg import router as tyre_degradation_router
from predictionGame import router as prediction_router

CACHE_DIR = Path(os.getenv("FASTF1_CACHE_DIR", Path(__file__).parent / ".fastf1-cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.configure(cache_dir=str(CACHE_DIR))

app = FastAPI(
    title="LapTrack F1 API",
    version="1.0.0",
    description="Race, driver, tyre and season analysis powered by FastF1.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8081,http://localhost:19006").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "service": "LapTrack F1 API", "version": app.version}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(DataNotLoadedError)
def timing_data_unavailable(_: Request, __: DataNotLoadedError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Formula 1 timing data is unavailable. LapTrack requires "
                "FastF1 3.9+ and an active F1TV Access, Pro or Premium account."
            )
        },
    )

app.include_router(race_summary_router)
app.include_router(average_lap_router)
app.include_router(sector_times_router)
app.include_router(sector_comparison_router)
app.include_router(perfect_lap_router)
app.include_router(pace_evolution_router)
app.include_router(tyre_degradation_router)
app.include_router(prediction_router)
