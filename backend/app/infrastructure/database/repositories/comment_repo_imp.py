from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.application.ports.repositories.comment_repository import CommentRepository
from backend.app.application.ports.repositories.log_repository import LogRepository
from backend.app.domain.entities import comment, log
from backend.app.infrastructure.models.comment import Comment as DBComment


class SQLAlchemyCommentRepository(CommentRepository):
    def __init__(self, db_session: Session, log_repository: LogRepository):
        self.db_session = db_session
        self.log_repository = log_repository

    def create_comment(self, comment: comment.Comment) -> comment.Comment:
        try:
            db_comment = DBComment(
                content=comment.content,
                author_id=comment.author_id,
                incident_id=comment.incident_id,
                timestamp=comment.timestamp,
            )
            self.db_session.add(db_comment)
            self.db_session.commit()
            self.db_session.refresh(db_comment)

            self.log_repository.create_log(log.Log(
                message=f"Comment created with ID {db_comment.id} for incident ID {comment.incident_id}",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))

            return self._to_domain_entity(db_comment)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to create comment for incident ID {comment.incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def get_comment_by_id(self, comment_id: int) -> Optional[comment.Comment]:
        try:
            db_comment = self.db_session.query(DBComment).filter_by(id=comment_id).first()
            if db_comment:
                return self._to_domain_entity(db_comment)
            return None
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to retrieve comment with ID {comment_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def update_comment(self, comment: comment.Comment) -> comment.Comment:
        try:
            db_comment = self.db_session.query(DBComment).filter_by(id=comment.id).first()
            if not db_comment:
                raise ValueError("Comment not found")

            db_comment.content = comment.content
            db_comment.timestamp = comment.timestamp
            self.db_session.commit()
            self.log_repository.create_log(log.Log(
                message=f"Comment with ID {comment.id} updated for incident ID {comment.incident_id}",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))
            return self._to_domain_entity(db_comment)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to update comment with ID {comment.id} for incident ID {comment.incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_comment(self, comment_id: int) -> None:
        try:
            db_comment = self.db_session.query(DBComment).filter_by(id=comment_id).first()
            if not db_comment:
                raise ValueError("Comment not found")
            self.db_session.delete(db_comment)
            self.db_session.commit()
            self.log_repository.create_log(log.Log(
                message=f"Comment with ID {comment_id} deleted for incident ID {db_comment.incident_id}",
                log_level=log.LogLevel.INFO,
                timestamp=datetime.now()
            ))
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.log_repository.create_log(log.Log(
                message=f"Failed to delete comment with ID {comment_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_comments_by_incident_id(self, incident_id: int) -> List[comment.Comment]:
        try:
            db_comments = self.db_session.query(DBComment).filter_by(incident_id=incident_id).all()
            return [self._to_domain_entity(db_comment) for db_comment in db_comments]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list comments for incident ID {incident_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def list_comments_by_author_id(self, author_id: int) -> List[comment.Comment]:
        try:
            db_comments = self.db_session.query(DBComment).filter_by(author_id=author_id).all()
            return [self._to_domain_entity(db_comment) for db_comment in db_comments]
        except SQLAlchemyError as e:
            self.log_repository.create_log(log.Log(
                message=f"Failed to list comments for author ID {author_id}: {str(e)}",
                log_level=log.LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            raise RuntimeError(f"Database error: {str(e)}")

    def _to_domain_entity(self, db_comment: DBComment) -> comment.Comment:
        return comment.Comment(
            id=db_comment.id,
            content=db_comment.content,
            author_id=db_comment.author_id,
            incident_id=db_comment.incident_id,
            timestamp=db_comment.timestamp
        )
