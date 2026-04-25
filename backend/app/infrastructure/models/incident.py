from datetime import datetime
from app.domain.enums.severity import Severity
from app.domain.enums.state import State
from app.infrastructure.database.base import Base
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    severity: Mapped[Severity] = mapped_column(SAEnum(Severity), nullable=False)
    state: Mapped[State] = mapped_column(SAEnum(State), nullable=False)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="incident")
    assigned_user: Mapped["User"] = relationship("User", back_populates="incidents", foreign_keys=[assigned_to])