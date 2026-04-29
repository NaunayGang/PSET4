from datetime import datetime
from backend.app.domain.enums.role import Role
from backend.app.infrastructure.database.base import Base
from sqlalchemy import String, DateTime, Enum as SAEnum, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .comment import Comment
    from .incident import Incident

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author")
    incidents: Mapped[list["Incident"]] = relationship("Incident", back_populates="assigned_user")