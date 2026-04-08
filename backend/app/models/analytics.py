import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AnalyticsStudentScore(Base):
    __tablename__ = "analytics_student_scores"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    dropout_risk: Mapped[float | None] = mapped_column(Numeric(5, 2))
    performance_risk: Mapped[float | None] = mapped_column(Numeric(5, 2))
    attendance_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    avg_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    gpa_trend: Mapped[str | None] = mapped_column(String(20))
    risk_factors: Mapped[dict | None] = mapped_column(JSON)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AnalyticsProgramScore(Base):
    __tablename__ = "analytics_program_scores"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, unique=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    performance_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    completion_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    pass_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    avg_gpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    dropout_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    enrollment_trend: Mapped[str | None] = mapped_column(String(20))
    relevance_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    demand_trend: Mapped[str | None] = mapped_column(String(20))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AnalyticsInstitutionKPI(Base):
    __tablename__ = "analytics_institution_kpis"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    total_students: Mapped[int | None] = mapped_column(Integer)
    active_students: Mapped[int | None] = mapped_column(Integer)
    total_programs: Mapped[int | None] = mapped_column(Integer)
    avg_gpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    overall_attendance: Mapped[float | None] = mapped_column(Numeric(5, 2))
    overall_pass_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    overall_dropout_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    at_risk_students: Mapped[int | None] = mapped_column(Integer)
    high_risk_students: Mapped[int | None] = mapped_column(Integer)
    avg_program_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    avg_relevance_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
