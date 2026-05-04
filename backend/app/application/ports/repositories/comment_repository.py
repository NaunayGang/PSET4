from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.domain.entities import comment


class CommentRepository(ABC):
    @abstractmethod
    def create_comment(self, comment: comment.Comment) -> comment.Comment:
        pass

    @abstractmethod
    def get_comment_by_id(self, comment_id: int) -> Optional[comment.Comment]:
        pass

    @abstractmethod
    def update_comment(self, comment: comment.Comment) -> comment.Comment:
        pass

    @abstractmethod
    def delete_comment(self, comment_id: int) -> None:
        pass

    @abstractmethod
    def list_comments_by_incident_id(self, incident_id: int) -> List[comment.Comment]:
        pass

    @abstractmethod
    def list_comments_by_author_id(self, author_id: int) -> List[comment.Comment]:
        pass
