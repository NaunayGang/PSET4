from abc import ABC, abstractmethod

from backend.app.domain.entities import Comment


class AddCommentPort(ABC):
    @abstractmethod
    def present_comment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def present_not_found(self, incident_id: int) -> None:
        pass

    @abstractmethod
    def present_failure(self, error_message: str) -> None:
        pass
