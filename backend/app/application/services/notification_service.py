from datetime import datetime

from backend.app.application.events.incident_event import IncidentEvent, IncidentEventType
from backend.app.domain.entities import Notification
from backend.app.domain.enums import Role, Severity


class InMemoryNotificationDispatcher:
    def __init__(self) -> None:
        self.sent_notifications: list[Notification] = []

    def dispatch(self, notification: Notification) -> None:
        self.sent_notifications.append(notification)


class NotificationService:
    def __init__(self, user_repository, notification_repository, dispatcher: InMemoryNotificationDispatcher | None = None):
        self.user_repository = user_repository
        self.notification_repository = notification_repository
        self.dispatcher = dispatcher or InMemoryNotificationDispatcher()

    def register(self, event_bus) -> None:
        event_bus.subscribe(IncidentEventType.INCIDENT_CREATED, self._handle_incident_created)
        event_bus.subscribe(IncidentEventType.INCIDENT_ASSIGNED, self._handle_incident_assigned)
        event_bus.subscribe(IncidentEventType.SEVERITY_CHANGED, self._handle_severity_changed)
        event_bus.subscribe(IncidentEventType.INCIDENT_RESOLVED, self._handle_incident_resolved)

    def _handle_incident_created(self, event: IncidentEvent) -> None:
        payload = event.payload or {}
        severity = payload.get("severity")
        if severity != Severity.CRITICAL.value:
            return

        recipients = self._users_with_roles({Role.INCIDENT_COMMANDER, Role.MANAGER})
        message = f"Critical incident {event.incident_id} was created and needs immediate attention."
        self._create_for_recipients(recipients, event, message)

    def _handle_incident_assigned(self, event: IncidentEvent) -> None:
        payload = event.payload or {}
        assignee_id = payload.get("assignee_id")
        if assignee_id is None:
            return
        message = f"Incident {event.incident_id} has been assigned to you."
        self._create_for_recipients({assignee_id}, event, message)

    def _handle_severity_changed(self, event: IncidentEvent) -> None:
        recipients = self._users_with_roles({Role.INCIDENT_COMMANDER, Role.MANAGER})
        payload = event.payload or {}
        new_severity = payload.get("new_severity", "unknown")
        message = f"Severity for incident {event.incident_id} changed to {new_severity}."
        self._create_for_recipients(recipients, event, message)

    def _handle_incident_resolved(self, event: IncidentEvent) -> None:
        payload = event.payload or {}
        creator_id = payload.get("creator_id")
        recipients = self._users_with_roles({Role.MANAGER})
        if creator_id is not None:
            recipients.add(creator_id)
        message = f"Incident {event.incident_id} has been resolved."
        self._create_for_recipients(recipients, event, message)

    def _create_for_recipients(self, recipients: set[int], event: IncidentEvent, message: str) -> None:
        for user_id in recipients:
            notification = Notification(
                user_id=user_id,
                incident_id=event.incident_id,
                event_type=event.event_type.value,
                message=message,
                created_at=datetime.now(),
            )
            stored = self.notification_repository.create_notification(notification)
            self.dispatcher.dispatch(stored)

    def _users_with_roles(self, roles: set[Role]) -> set[int]:
        users = self.user_repository.list_users()
        return {user.id for user in users if user.role in roles}
