# ERGuide — ER Recommender System

ERGuide is a web application that helps users find nearby hospitals with minimal wait times, forecasts ER overcrowding, and provides data-driven recommendations. Built with **FastAPI**, **React**, **PostgreSQL**, and **APScheduler**.

## Repository structure

```
├── backend/          # FastAPI application (Python 3.11)
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, logging, security
│   │   ├── db/       # SQLAlchemy models & Alembic migrations
│   │   ├── ingestion/# Data ingestion pipeline
│   │   ├── jobs/     # Scheduled jobs (ingestion, forecasting, evaluation)
│   │   ├── ml/       # Machine-learning & forecasting modules
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic (geocoding, routing, forecasts)
│   │   └── utils/    # Shared helpers
│   └── tests/
├── frontend/         # React + TypeScript + Vite
│   └── src/
├── infra/            # Infrastructure docs
├── docker-compose.yml
└── .env.example
```

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker & Docker Compose | latest | Required for the containerised workflow |
| Python | 3.11+ | Only needed when running the backend outside Docker or running tests |
| Node.js | 20+ | Only needed when running the frontend outside Docker |
| PostgreSQL | 14+ | Provide a connection string via `DATABASE_URL` |

## Environment setup

1. Copy the example env file and fill in your values:

   ```bash
   cp .env.example .env
   ```

2. Required variables (see `.env.example` for the full list):

   | Variable | Description | Default |
   |----------|-------------|---------|
   | `DATABASE_URL` | PostgreSQL connection string | *(required)* |
   | `ENVIRONMENT` | `dev` or `prod` — controls APScheduler startup | `dev` |
   | `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |
   | `VITE_API_URL` | Base URL the frontend uses for API calls | `/api` |
   | `VITE_API_TARGET` | Backend target for the Vite dev-server proxy | `http://backend:8000` |

## Running with Docker Compose

```bash
git clone https://github.com/agbjonathan/er-recommder-system
cd er-recommder-system
cp .env.example .env
# Edit .env with your DATABASE_URL and any other overrides
docker compose up --build
```

Once the containers are running:

- **Frontend** → [http://localhost:3000](http://localhost:3000)
- **Backend (Swagger docs)** → [http://localhost:8000/docs](http://localhost:8000/docs)

## Running services individually

See the individual READMEs for more detail:

### Backend — uvicorn

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend — npm

```bash
cd frontend
npm install
npm run dev
```

> **Note:** When running services individually, set `VITE_API_TARGET=http://localhost:8000` in your `.env` (instead of `http://backend:8000`) so the Vite proxy reaches the local backend.

## Running tests

```bash
cd backend
source venv/bin/activate
pytest
```

## Useful Docker commands

```bash
# View logs
docker compose logs -f

# Rebuild containers after dependency changes
docker compose up --build

# Stop all services
docker compose down

# Force-recreate after .env changes
docker compose up --force-recreate
```

## Branch structure

| Branch | Purpose |
|--------|---------|
| `main` | Primary development branch — all feature PRs target here |
| `azure` | Deployment branch — **never commit directly to `azure`**; merge from `main` only |

## License

See [LICENSE](LICENSE) for details.
