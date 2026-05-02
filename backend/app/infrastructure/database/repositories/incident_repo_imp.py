from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.domain.entities import incident, log
from backend.app.application.ports.repositories.incident_repository import IncidentRepository
from backend.app.application.ports.repositories.log_repository import LogRepository
from backend.app.infrastructure.models.incident import Incident as DBIncident


class SQLAlchemyIncidentRepository(IncidentRepository):
    def __init__(self, db_session: Session, log_repository: LogRepository):
        self.db_session = db_session
        self.log_repository = log_repository

    def create_incident(self, incident: incident.Incident) -> incident.Incident:
        try:
            db_incident = DBIncident(
                title=incident.title,
                description=incident.description,
                severity=incident.severity,
                state=incident.state,
                assigned_to=incident.assigned_to,
                created_at=incident.created_at,
                updated_at=incident.updated_at
            )
            self.db_session.add(db_incident)
            self.db_session.commit()
            self.db_session.refresh(db_incident)
            self.log_repository.create_log(log.Log(
                message=f"Incident created with ID {db_incident.id}",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))
            return self._to_domain_entity(db_incident)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to create incident: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def get_incident_by_id(self, incident_id: int) -> Optional[incident.Incident]:
        try:
            db_incident = self.db_session.query(DBIncident).filter_by(id=incident_id).first()
            if db_incident:
                return self._to_domain_entity(db_incident)
            return None
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to retrieve incident with ID {incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def update_incident(self, incident: incident.Incident) -> incident.Incident:
        try:
            db_incident = self.db_session.query(DBIncident).filter_by(id=incident.id).first()
            if not db_incident:
                raise ValueError("Incident not found")

            db_incident.title = incident.title
            db_incident.description = incident.description
            db_incident.state = incident.state
            db_incident.severity = incident.severity
            db_incident.assigned_to = incident.assigned_to
            db_incident.updated_at = incident.updated_at

            self.db_session.commit()
            self.log_repository.create_log(log.Log(
                message=f"Incident with ID {db_incident.id} updated",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))
            return self._to_domain_entity(db_incident)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to update incident with ID {incident.id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_incident(self, incident_id: int) -> None:
        try:
            db_incident = self.db_session.query(DBIncident).filter_by(id=incident_id).first()
            if not db_incident:
                raise ValueError("Incident not found")

            self.db_session.delete(db_incident)
            self.db_session.commit()
            self.log_repository.create_log(log.Log(
                message=f"Incident with ID {incident_id} deleted",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to delete incident with ID {incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_incidents(self) -> List[incident.Incident]:
        try:
            db_incidents = self.db_session.query(DBIncident).all()
            return [self._to_domain_entity(db_incident) for db_incident in db_incidents]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list incidents: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_incidents_by_assigned_user(self, user_id: int) -> List[incident.Incident]:
        try:
            db_incidents = self.db_session.query(DBIncident).filter_by(assigned_to=user_id).all()
            return [self._to_domain_entity(db_incident) for db_incident in db_incidents]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list incidents assigned to user ID {user_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_incidents_by_severity(self, severity: incident.Severity) -> List[incident.Incident]:
        try:
            db_incidents = self.db_session.query(DBIncident).filter_by(severity=severity).all()
            return [self._to_domain_entity(db_incident) for db_incident in db_incidents]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list incidents with severity {severity}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_incidents_by_state(self, state: incident.State) -> List[incident.Incident]:
        try:
            db_incidents = self.db_session.query(DBIncident).filter_by(state=state).all()
            return [self._to_domain_entity(db_incident) for db_incident in db_incidents]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list incidents with state {state}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def _to_domain_entity(self, db_incident: DBIncident) -> incident.Incident:
        return incident.Incident(
            id=db_incident.id,
            title=db_incident.title,
            description=db_incident.description,
            state=db_incident.state,
            severity=db_incident.severity,
            assigned_to=db_incident.assigned_to,
            created_at=db_incident.created_at,
            updated_at=db_incident.updated_at,
            summary_id=db_incident.summary_id
        )
