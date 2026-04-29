# Database Migrations

## Overview

Database schema versioning is managed with [Alembic](https://alembic.sqlalchemy.org/).

## Migration Flow

```
Container Start → Wait for DB → Run Migrations → Seed Data → Start App
```

## Common Commands

### Create a New Migration

```bash
cd backend
alembic revision -m "add_new_table"
```

### Run Migrations Manually

```bash
cd backend
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1        # Rollback last migration
alembic downgrade base       # Rollback all migrations
```

### Show Current Version

```bash
alembic current
```

### Show Migration History

```bash
alembic history
```

## Auto-run on Docker Startup

The backend container automatically runs migrations on startup via `scripts/start.sh`. This script:

1. Waits for PostgreSQL to be ready
2. Runs `alembic upgrade head`
3. Seeds default data
4. Starts the application

## Seed Data

The `scripts/seed.py` script creates:

### Test Users

| Username | Role |
|----------|------|
| operator1 | OPERATOR |
| commander1 | INCIDENT_COMMANDER |
| responder1 | TECHNICAL_RESPONDER |
| manager1 | MANAGER |
| admin1 | ADMIN |

**Note**: All test users have `disabled_for_testing_only` as password hash. Auth is not yet implemented.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://incidentflow:incidentflow@db:5432/incidentflow | Database connection string |
| POSTGRES_USER | incidentflow | PostgreSQL username |
| POSTGRES_PASSWORD | incidentflow | PostgreSQL password |
| POSTGRES_DB | incidentflow | PostgreSQL database name |