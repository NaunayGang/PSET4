FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY scripts/start.sh ./scripts/
RUN chmod +x scripts/start.sh

EXPOSE 8000

ENV POSTGRES_USER=incidentflow
ENV POSTGRES_PASSWORD=incidentflow
ENV POSTGRES_DB=incidentflow

CMD ["./scripts/start.sh"]
