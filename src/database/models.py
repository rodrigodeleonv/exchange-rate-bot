from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.base import Base


class Institution(Base):
    """Institution model for storing bank/financial institution information."""

    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Metadata

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship

    exchange_rates: Mapped[list["ExchangeRate"]] = relationship(
        "ExchangeRate", back_populates="institution"
    )

    def __repr__(self) -> str:
        return f"<Institution(id={self.id}, name='{self.name}')>"

    __table_args__ = (Index("idx_institution_name", "name"),)


class ExchangeRate(Base):
    """ExchangeRate model for storing exchange rate information."""

    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to Institution

    institution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("institutions.id"), nullable=False
    )

    # Exchange rate information

    buy_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)

    # Metadata

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship

    institution: Mapped["Institution"] = relationship(
        "Institution", back_populates="exchange_rates"
    )

    def __repr__(self) -> str:
        return (
            f"<ExchangeRate(id={self.id}, institution_id={self.institution_id}, "
            f"buy_rate={self.buy_rate}, recorded_at={self.recorded_at})>"
        )

    __table_args__ = (
        Index("idx_exchange_rate_institution", "institution_id"),
        Index("idx_exchange_rate_recorded_at", "recorded_at"),
    )
