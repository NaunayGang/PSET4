from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.enums.log_level import LogLevel
from backend.app.infrastructure.database.base import Base


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_level: Mapped[LogLevel] = mapped_column(SAEnum(LogLevel), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    message: Mapped[str] = mapped_column(String(1000), nullable=False)

