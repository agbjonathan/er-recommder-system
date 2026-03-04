# Frontend — ER Recommender System

React + TypeScript single-page application for the ER Recommender System. Built with **Vite**, **Tailwind CSS v4**, **React Router**, **Leaflet** (maps), and **Recharts** (charts).

## Prerequisites

- Node.js 20+
- A `.env` file at the repo root (see the root [README](../README.md) and [.env.example](../.env.example))

## Getting started

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
