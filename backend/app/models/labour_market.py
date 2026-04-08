import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class LabourMarketTrend(Base):
    __tablename__ = "labour_market_trends"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    occupation: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100), default="Azerbaijan")
    demand_level: Mapped[str | None] = mapped_column(String(20))
    growth_rate: Mapped[float | None] = mapped_column(Numeric(6, 2))
    avg_salary_azn: Mapped[float | None] = mapped_column(Numeric(10, 2))
    job_postings: Mapped[int | None] = mapped_column(Integer)
    data_source: Mapped[str | None] = mapped_column(String(255))
    observed_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class SkillTrend(Base):
    __tablename__ = "skill_trends"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    demand_level: Mapped[str | None] = mapped_column(String(20))
    growth_rate: Mapped[float | None] = mapped_column(Numeric(6, 2))
    relevance_to: Mapped[str | None] = mapped_column(Text)  # comma-separated list
    future_outlook: Mapped[str | None] = mapped_column(String(20))
    data_source: Mapped[str | None] = mapped_column(String(255))
    observed_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
