# Frontend — ER Recommender System

React + TypeScript single-page application for the ER Recommender System. Built with **Vite**, **Tailwind CSS v4**, **React Router**, **Leaflet** (maps), and **Recharts** (charts).

## Production deployment

The frontend is deployed as an **Azure Static Web App**. Pushing to the `azure` branch triggers an automatic build and deploy via the GitHub Actions workflow.

### GitHub Secrets required

| Secret | Description |
|--------|-------------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN_RED_POND_0BD3F550F` | Deploy token for the Static Web App |
| `VITE_API_URL` | Production API base URL (injected at build time) |

### Deploy

```bash
git checkout azure
git merge main
git push origin azure
```

> **Important:** Always verify the backend is healthy (`/api/health` returns 200) **before** deploying the frontend. See the root [README](../README.md) for the full deploy sequence.

## Local development

### Prerequisites

- Node.js 20+
- A `.env` file at the repo root (see [.env.example](../.env.example) on the `main` branch)

### Getting started

```bash
cd frontend
npm install
npm run dev
```

The app will be served at [http://localhost:3000](http://localhost:3000).

> **Note:** When running outside Docker Compose, set `VITE_API_TARGET=http://localhost:8000` in the repo-root `.env` so the Vite dev-server proxy reaches the local backend instead of the Docker service name.

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Base URL used by the frontend for API calls | `/api` |
| `VITE_API_TARGET` | Backend URL the Vite proxy forwards `/api` requests to | `http://localhost:8000` |

## Available scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start the Vite dev server with HMR |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint |

## Project layout

```
src/
├── api/         # Axios API client
├── components/  # Reusable UI components (FeedbackWidget, …)
├── i18n/        # Internationalisation (LangContext, translations)
├── pages/       # Route pages (Home, Dashboard, Docs)
├── assets/      # Static assets
├── App.tsx      # Root component & router
└── main.tsx     # Entry point
```
