# Backend — ER Recommender System API

FastAPI application that powers the ER Recommender System. Provides endpoints for hospital recommendations, ER congestion forecasting, geocoding, and a dashboard API.

## Tech stack

- **FastAPI** — async REST API
- **SQLAlchemy 2 + Alembic** — ORM & database migrations
- **APScheduler** — background jobs (ingestion, forecasting, evaluation)
- **statsmodels / pandas / NumPy** — ML forecasting pipeline
- **PostgreSQL** — primary data store

## Prerequisites

- Python 3.11+
- A running PostgreSQL instance
- A `.env` file at the repo root (see the root [README](../README.md) and [.env.example](../.env.example))

## Getting started

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
