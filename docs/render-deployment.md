# Render Deployment

## Overview

Deployment to Render using Docker images pushed via CI/CD.

## Services

### Dev Environment
- `incidentflow-backend-dev`
- `incidentflow-frontend-dev`
- `incidentflow-db-dev` (managed PostgreSQL)

### Prod Environment
- `incidentflow-backend-prod`
- `incidentflow-frontend-prod`
- `incidentflow-db-prod` (managed PostgreSQL)

## Docker Images

| Service | Dev Tag | Prod Tag |
|---------|---------|----------|
| Backend | `naunaygang/incidentflow/backend:dev` | `naunaygang/incidentflow/backend:latest` |
| Frontend | `naunaygang/incidentflow/frontend:dev` | `naunaygang/incidentflow/frontend:latest` |

## Environment Variables

### Backend
| Variable | Dev | Prod |
|----------|-----|------|
| `DATABASE_URL` | Render managed DB URL | Render managed DB URL |
| `DEBUG` | `true` | `false` |

### Frontend
| Variable | Value |
|----------|-------|
| `BACKEND_URL` | Backend service URL (e.g., `https://incidentflow-backend.onrender.com`) |

## Render Setup

### 1. Create PostgreSQL Services
1. Go to Render Dashboard → New → PostgreSQL
2. Create two instances: `incidentflow-db-dev` and `incidentflow-db-prod`
3. Copy connection strings after creation

### 2. Create Backend Service (repeat for dev/prod)
1. New → Blueprint → Upload `render.yaml` or manually create Web Service
2. Docker image: `naunaygang/incidentflow/backend:dev` (dev) / `:latest` (prod)
3. Add environment variables from table above
4. Set health check path: `/health` (if endpoint exists)

### 3. Create Frontend Service (repeat for dev/prod)
1. New → Web Service
2. Docker image: `naunaygang/incidentflow/frontend:dev` (dev) / `:latest` (prod)
3. Add `BACKEND_URL` pointing to backend service

### 4. Enable Auto-Deploy
1. In each service → Settings → Auto-Deploy → Connect GitHub repo
2. Set branch: `dev/*` for dev, `main` for prod

### 5. Get Deploy Hook URLs
1. In each service → Settings → Deploy Hooks
2. Copy the webhook URL
3. Add as GitHub secret: `RENDER_DEPLOY_HOOK_DEV` / `RENDER_DEPLOY_HOOK_PROD`

## CI/CD Integration

After pushing Docker images, CI triggers Render deploy hooks:

```bash
curl -X POST $RENDER_DEPLOY_HOOK_URL
```

## Manual Deployment

To manually trigger a deploy:
```bash
curl -X POST https://api.render.com/deploy-to-hook?key=<hook-id>
```

## Rollback

In Render dashboard, go to service → Deploys → select previous successful deploy → click "Deploy">