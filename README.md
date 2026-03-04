# ERGuide — Azure Deployment Guide

Production deployment documentation for the ER Recommender System on Azure.

> **This README is for the `azure` branch.** For local development instructions, see the `main` branch README.

## Production architecture

```
┌──────────────┐       ┌───────────────────────┐       ┌─────────────────┐
│   Frontend   │──────▶│  Backend (FastAPI)     │──────▶│   Supabase      │
│  Azure SWA   │  /api │  Azure Container App  │       │   PostgreSQL    │
└──────────────┘       └───────────────────────┘       └─────────────────┘
     ▲                          ▲
     │ auto-deploy              │ manual push
     │ on push to azure         │
     ▼                          ▼
  GitHub Actions           Azure Container
  (SWA workflow)           Registry (ACR)
```

- **Backend** → Azure Container App ← pulls image from Azure Container Registry (ACR)
- **Frontend** → Azure Static Web Apps ← auto-deploys from the `azure` branch via GitHub Actions
- **Database** → Supabase PostgreSQL

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in (`az login`)
- Docker installed
- Access to the ACR and Container App resources in the Azure subscription
- GitHub repository secrets configured:
  - `VITE_API_URL` — production API base URL
  - `AZURE_STATIC_WEB_APPS_API_TOKEN_RED_POND_0BD3F550F` — deploy token for Static Web Apps

## Required environment variables

These must be set on the **Azure Container App** (backend):

| Variable | Description | Value |
|----------|-------------|-------|
| `DATABASE_URL` | Production PostgreSQL connection string (Supabase) | `postgresql://…` |
| `ALLOWED_ORIGINS` | Frontend URL for CORS | `https://<swa-hostname>.azurestaticapps.net` |
| `ENVIRONMENT` | Must be `prod` — disables APScheduler (jobs run via Azure Container App Jobs) | `prod` |

## Deploy sequence

> **Important:** Always deploy the **backend first**, then the frontend. The frontend's geocoding proxy depends on a reachable backend API. Deploying frontend before backend can break the live site.

### Step 1 — Deploy backend

```bash
# 1. Log in to Azure and ACR
az login
az acr login --name <acr-name>

# 2. Build and push the Docker image
docker build -t <acr-name>.azurecr.io/er-backend:latest ./backend
docker push <acr-name>.azurecr.io/er-backend:latest

# 3. Update the Container App with the new image
az containerapp update \
  --name <container-app-name> \
  --resource-group <resource-group> \
  --image <acr-name>.azurecr.io/er-backend:latest

# 4. (If needed) Update environment variables
az containerapp update \
  --name <container-app-name> \
  --resource-group <resource-group> \
  --set-env-vars \
    ALLOWED_ORIGINS=https://<swa-hostname>.azurestaticapps.net \
    ENVIRONMENT=prod \
    DATABASE_URL=<connection-string>
```

### Step 2 — Verify backend (mandatory before frontend deploy)

```bash
curl https://<container-app-hostname>/api/health
```

You should receive a `200 OK` response. **Do not proceed to step 3 until the health check passes.**

### Step 3 — Deploy frontend

The frontend auto-deploys via GitHub Actions when changes are pushed to the `azure` branch:

```bash
git checkout azure
git merge main
git push origin azure
```

Monitor the deployment in the **Actions** tab of the GitHub repository.

## Smoke test checklist

After both services are deployed, verify end-to-end functionality:

- [ ] **Health endpoint** — `GET /api/health` returns `200`
- [ ] **Search** — enter an address and confirm hospital results appear
- [ ] **Locate button** — click the locate/geolocation button and verify it resolves your position
- [ ] **Empty state** — search a remote or invalid location and confirm the empty-state message displays
- [ ] **Resolved location banner** — after geolocation, confirm the resolved address banner appears
- [ ] **Network tab** — open browser DevTools → Network and confirm all `/api/*` requests return `200` (no CORS or 5xx errors)

## Useful Azure CLI commands

```bash
# Stream live logs from the container app
az containerapp logs show \
  --name <container-app-name> \
  --resource-group <resource-group> \
  --follow

# List current environment variables
az containerapp show \
  --name <container-app-name> \
  --resource-group <resource-group> \
  --query "properties.template.containers[0].env" \
  -o table

# Force restart the container app
az containerapp revision restart \
  --name <container-app-name> \
  --resource-group <resource-group> \
  --revision <revision-name>

# List revisions
az containerapp revision list \
  --name <container-app-name> \
  --resource-group <resource-group> \
  -o table
```

## Branch structure

| Branch | Purpose |
|--------|---------|
| `main` | Primary development branch — all feature PRs target here |
| `azure` | Deployment branch — **never commit directly to `azure`**; merge from `main` only |
