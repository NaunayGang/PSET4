from pydantic import BaseModel


class IncidentDTO(BaseModel):
    id: int
    title: str
    description: str | None
    severity: str
    state: str
    assigned_to: int | None
    created_at: str
    updated_at: str | None
    summary_id: int | None
