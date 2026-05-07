from app.interface.controllers.incident_controller import router as incident_router
from fastapi import FastAPI

app = FastAPI(title="IncidentFlow API")

app.include_router(incident_router)
