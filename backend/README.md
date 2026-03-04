# Backend — ER Recommender System API

FastAPI application that powers the ER Recommender System. Provides endpoints for hospital recommendations, ER congestion forecasting, geocoding, and a dashboard API.

## Tech stack

- **FastAPI** — async REST API
- **SQLAlchemy 2 + Alembic** — ORM & database migrations
- **APScheduler** — background jobs in dev (disabled in production; Azure Container App Jobs used instead)
- **statsmodels / pandas / NumPy** — ML forecasting pipeline
- **PostgreSQL** — primary data store (Supabase in production)

## Production deployment

The backend runs as an **Azure Container App**, pulling images from Azure Container Registry. See the root [README](../README.md) for the full deploy sequence.

Key production settings:
- `ENVIRONMENT=prod` — disables APScheduler
- `ALLOWED_ORIGINS` — set to the Static Web App URL for CORS
- `DATABASE_URL` — Supabase PostgreSQL connection string

## Local development

### Prerequisites

- Python 3.11+
- A running PostgreSQL instance
- A `.env` file at the repo root (see [.env.example](../.env.example) on the `main` branch)

### Getting started

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.dev.txt    # includes production + test deps
```

### Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Run database migrations

```bash
alembic -c app/db/alembic.ini upgrade head
```

### Run tests

```bash
pytest
```

Test configuration lives in `pytest.ini`.

## Project layout

```
app/
├── api/         # Route handlers (health, recommend, hospitals, forecasts, …)
├── core/        # Config, logging, security middleware
├── db/          # SQLAlchemy models, session, Alembic migrations
├── ingestion/   # Data fetching & parsing pipeline
├── jobs/        # Scheduled background jobs
├── ml/          # Forecasting models, feature engineering, evaluation
├── schemas/     # Pydantic request/response schemas
├── services/    # Business logic (geocoding, routing, forecast storage)
├── utils/       # Shared helpers (math, time)
├── main.py      # App entrypoint & lifespan setup
└── scheduler.py # APScheduler configuration
tests/
├── test_api/
├── test_db/
├── test_ml/
└── test_scheduler/
```
