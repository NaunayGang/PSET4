from datetime import datetime
from backend.app.infrastructure.database.base import Base
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    content: Mapped[str] = mapped_column(String(1000), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="comments")
    incident: Mapped["Incident"] = relationship("Incident", back_populates="comments")