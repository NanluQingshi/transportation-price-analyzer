from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    airline: Mapped[str | None] = mapped_column(String(10), nullable=True)
    flight_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CNY")
    cabin_class: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
