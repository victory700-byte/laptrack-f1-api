# LapTrack F1 API

FastAPI service for LapTrack's race summaries, lap and sector comparisons, tyre degradation, season pace and prediction scoring.

## Requirements

Formula 1 began requiring authentication for archived timing data in October 2026. Live lap analysis therefore requires:

- FastF1 3.9 or newer
- An active F1TV Access, Pro or Premium subscription
- `F1_USERNAME` and `F1_PASSWORD` configured as private server environment variables

FastF1 stores a short-lived authentication token and cached timing data. Credentials are sent to Formula 1 by FastF1 and must never be exposed to the frontend.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn api:app --reload
```

The API runs at `http://127.0.0.1:8000`, health is at `/health`, and interactive documentation is at `/docs`.

## Tests

```bash
python -m unittest discover -s tests
```

## Deployment

`render.yaml` defines a Render web service. Configure `ALLOWED_ORIGINS`, `F1_USERNAME` and `F1_PASSWORD` in the hosting provider. The FastF1 cache directory should use persistent storage in production when available.
