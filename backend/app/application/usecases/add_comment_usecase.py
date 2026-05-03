from datetime import datetime

from backend.app.application.ports.add_comment_port import AddCommentPort
from backend.app.domain.entities import Comment, Log
from backend.app.domain.enums import LogLevel, Role


class AddCommentUseCase:
    def __init__(self, incident_repository, user_repository, comment_repository, log_repository):
        self.incident_repository = incident_repository
        self.user_repository = user_repository
        self.comment_repository = comment_repository
        self.log_repository = log_repository

    def execute(self, incident_id: int, user_id: int, content: str, output_port: AddCommentPort) -> None:
        # Fetch the incident and user from the repositories
        incident = self.incident_repository.get_incident_by_id(incident_id)
        user = self.user_repository.get_user_by_id(user_id)
        user_role = user.role if user else "Unknown"

        if not incident:
            output_port.present_not_found(incident_id)
            return

        if not user:
            output_port.present_failure(f"User with ID {user_id} not found.")
            return

        if user_role not in [Role.ADMIN, Role.OPERATOR, Role.TECHNICAL_RESPONDER]:
            output_port.present_failure(f"User with ID {user_id} does not have permission to add comments.")
            return

        try:
            # Create the comment.role != "admin" or user.id != incident.assigned_user_id:
            new_comment = Comment(
                id=0,  # ID will be set by the repository
                content=content,
                author_id=user.id,
                timestamp=datetime.now(),
                incident_id=incident.id
            )
            comment = self.comment_repository.create_comment(new_comment)

            # Log the addition of the comment
            log_message = f"Comment added to incident {incident.id} by user {user.name} (ID: {user.id})"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.INFO,
                timestamp=datetime.now()
            ))

            output_port.present_comment(comment)
        except Exception as e:
            log_message = f"Failed to add comment to incident {incident_id} by user {user_id}: {str(e)}"
            self.log_repository.create_log(Log(
                message=log_message,
                log_level=LogLevel.ERROR,
                timestamp=datetime.now()
            ))
            output_port.present_failure(str(e))
            raise ValueError(f"Failed to add comment: {str(e)}")
