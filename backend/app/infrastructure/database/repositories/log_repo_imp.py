from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.domain.entities import log
from backend.app.domain.repositories.log_repository import LogRepository
from backend.app.infrastructure.models.log import Log as DBLog


class SQLAlchemyLogRepository(LogRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_log(self, log: log.Log) -> log.Log:
        try:
            db_log = DBLog(
                message=log.message,
                level=log.log_level,
                timestamp=log.timestamp,
            )
            self.db_session.add(db_log)
            self.db_session.commit()
            self.db_session.refresh(db_log)
            return self._to_domain_entity(db_log)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")

    def get_log_by_id(self, log_id: int) -> Optional[log.Log]:
        try:
            db_log = self.db_session.query(DBLog).filter_by(id=log_id).first()
            if db_log:
                return self._to_domain_entity(db_log)
            return None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def list_logs(self) -> List[log.Log]:
        try:
            db_logs = self.db_session.query(DBLog).all()
            return [self._to_domain_entity(db_log) for db_log in db_logs]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def list_logs_by_level(self, log_level: log.LogLevel) -> List[log.Log]:
        try:
            db_logs = self.db_session.query(DBLog).filter_by(log_level=log_level).all()
            return [self._to_domain_entity(db_log) for db_log in db_logs]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def _to_domain_entity(self, db_log: DBLog) -> log.Log:
        return log.Log(
            id=db_log.id,
            message=db_log.message,
            log_level=db_log.log_level,
            timestamp=db_log.timestamp,
        )
