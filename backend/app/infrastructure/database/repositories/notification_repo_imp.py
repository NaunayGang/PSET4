from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.application.ports.repositories.notification_repository import (
    NotificationRepository,
)
from backend.app.domain.entities import Notification
from backend.app.infrastructure.models.notification import Notification as DBNotification


class SQLAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_notification(self, notification: Notification) -> Notification:
        try:
            db_notification = DBNotification(
                user_id=notification.user_id,
                incident_id=notification.incident_id,
                event_type=notification.event_type,
                message=notification.message,
                created_at=notification.created_at,
                read_at=notification.read_at,
            )
            self.db_session.add(db_notification)
            self.db_session.commit()
            self.db_session.refresh(db_notification)
            return self._to_domain_entity(db_notification)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")

    def list_notifications_by_user(self, user_id: int) -> List[Notification]:
        try:
            db_notifications = self.db_session.query(DBNotification).filter_by(user_id=user_id).all()
            return [self._to_domain_entity(db_notification) for db_notification in db_notifications]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def _to_domain_entity(self, db_notification: DBNotification) -> Notification:
        return Notification(
            id=db_notification.id,
            user_id=db_notification.user_id,
            incident_id=db_notification.incident_id,
            event_type=db_notification.event_type,
            message=db_notification.message,
            created_at=db_notification.created_at,
            read_at=db_notification.read_at,
        )
