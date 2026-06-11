from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class WatchedRoute(Base):
    __tablename__ = "watched_routes"
    __table_args__ = (UniqueConstraint("origin", "destination"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(3), nullable=False)
    destination: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
