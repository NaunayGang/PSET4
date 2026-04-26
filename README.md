# PSET4

## Environment Setup

1. Copy the template and create your local env file:

```bash
cp .env.example .env
```

2. Edit `.env` and set your local values. At minimum:

```env
DATABASE_URL=postgresql://app_user:YOUR_PASSWORD@localhost:5432/incident_flow_db
```

3. Run Alembic commands with this project's `DATABASE_URL`:

```bash
export DATABASE_URL=postgresql://app_user:YOUR_PASSWORD@localhost:5432/incident_flow_db
/home/niko/code/PSET4/.venv/bin/alembic current
/home/niko/code/PSET4/.venv/bin/alembic heads
/home/niko/code/PSET4/.venv/bin/alembic upgrade head
```

Notes:
- Do not commit `.env`.
- Commit `.env.example` only.
- Keep one dedicated database per project to avoid migration conflicts.