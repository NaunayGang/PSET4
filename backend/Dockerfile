FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY scripts/start.sh .
RUN chmod +x start.sh

EXPOSE 8000

ENV POSTGRES_USER=incidentflow
ENV POSTGRES_PASSWORD=incidentflow
ENV POSTGRES_DB=incidentflow

CMD ["./start.sh"]
