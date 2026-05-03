from abc import ABC, abstractmethod
from typing import List

from backend.app.domain.entities import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def create_notification(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def list_notifications_by_user(self, user_id: int) -> List[Notification]:
        pass
