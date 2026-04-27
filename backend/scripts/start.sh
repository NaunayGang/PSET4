#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\q' 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

cd /app

echo "Running database migrations..."
python -m alembic upgrade head

echo "Seeding database..."
python scripts/seed.py

echo "Starting application..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000