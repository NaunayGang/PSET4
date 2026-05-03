from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.application.ports.repositories.user_repository import UserRepository
from backend.app.domain.entities import User
from backend.app.infrastructure.models.user import User as DBUser


class SQLAlchemyUserRepository(UserRepository):

    def __init__(self, session: Session):
        self._session = session

    def create_user(self, user: User) -> User:
        try:
            db_user = DBUser(
                id=user.id,
                username=user.username,
                password_hash=user.password_hash,
                role=user.role,
                created_at=user.created_at,
                last_login=user.last_login
            )
            self._session.add(db_user)
            self._session.commit()
            self._session.refresh(db_user)
            return user
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            db_user = self._session.get(DBUser, user_id)
            if db_user:
                return User(
                    id=db_user.id,
                    username=db_user.username,
                    password_hash=db_user.password_hash,
                    role=db_user.role,
                    created_at=db_user.created_at,
                    last_login=db_user.last_login
                )
            return None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def update_user(self, user: User) -> User:
        try:
            db_user = self._session.get(DBUser, user.id)
            if db_user:
                db_user.username = user.username
                db_user.password_hash = user.password_hash
                db_user.role = user.role
                db_user.created_at = user.created_at
                db_user.last_login = user.last_login
            self._session.commit()
            self._session.refresh(db_user)
            return user
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")


    def delete_user(self, user_id: int) -> None:
        try:
            db_user = self._session.get(DBUser, user_id)
            if db_user:
                self._session.delete(db_user)
                self._session.commit()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")

    def list_users(self) -> List[User]:
        try:
            db_users = self._session.query(DBUser).all()
            return [
                User(
                    id=db_user.id,
                    username=db_user.username,
                    password_hash=db_user.password_hash,
                    role=db_user.role,
                    created_at=db_user.created_at,
                    last_login=db_user.last_login
                )
                for db_user in db_users
            ]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")
