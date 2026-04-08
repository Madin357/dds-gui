import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    credits: Mapped[float | None] = mapped_column(Numeric(4, 1))
    semester: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    program: Mapped["Program"] = relationship(back_populates="courses")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="course")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="course")


from app.models.program import Program  # noqa
from app.models.attendance import AttendanceRecord  # noqa
from app.models.assessment import Assessment  # noqa
