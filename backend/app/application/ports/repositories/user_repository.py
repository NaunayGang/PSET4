from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    def list_users(self) -> List[User]:
        pass
