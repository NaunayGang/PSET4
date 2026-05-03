from collections import defaultdict
from typing import Callable

from backend.app.application.events.incident_event import IncidentEvent, IncidentEventType

EventHandler = Callable[[IncidentEvent], None]


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[IncidentEventType, list[EventHandler]] = defaultdict(list)
        self.published_events: list[IncidentEvent] = []

    def subscribe(self, event_type: IncidentEventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: IncidentEvent) -> None:
        self.published_events.append(event)
        for handler in self._handlers.get(event.event_type, []):
            handler(event)
