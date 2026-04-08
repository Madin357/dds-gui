import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Boolean, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    student_code: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    enrollment_date: Mapped[date | None] = mapped_column(Date)
    current_gpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    current_semester: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    institution: Mapped["Institution"] = relationship(back_populates="students")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="student")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="student")
    statuses: Mapped[list["StudentStatus"]] = relationship(back_populates="student")


class StudentStatus(Base):
    __tablename__ = "student_statuses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="statuses")


from app.models.institution import Institution  # noqa
from app.models.enrollment import Enrollment  # noqa
from app.models.attendance import AttendanceRecord  # noqa
from app.models.assessment import Assessment  # noqa
