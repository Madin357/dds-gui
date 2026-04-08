import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    score: Mapped[float | None] = mapped_column(Numeric(6, 2))
    max_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=100)
    percentage: Mapped[float | None] = mapped_column(Numeric(5, 2))
    grade: Mapped[str | None] = mapped_column(String(5))
    assessed_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="assessments")
    course: Mapped["Course"] = relationship(back_populates="assessments")


from app.models.student import Student  # noqa
from app.models.course import Course  # noqa
