import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # exam, midterm, assignment, quiz, project, final
    title: Mapped[str | None] = mapped_column(String(255))
    score: Mapped[float | None] = mapped_column(Numeric(6, 2))
    max_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=100)
    percentage: Mapped[float | None] = mapped_column(Numeric(5, 2))
    grade: Mapped[str | None] = mapped_column(String(5))
    assessed_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="assessments")
    course: Mapped["Course"] = relationship(back_populates="assessments")


from app.models.student import Student  # noqa: E402, F401
from app.models.course import Course  # noqa: E402, F401
