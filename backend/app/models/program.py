import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    level: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(255))
    duration_months: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    institution: Mapped["Institution"] = relationship(back_populates="programs")
    courses: Mapped[list["Course"]] = relationship(back_populates="program")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="program")


from app.models.institution import Institution  # noqa
from app.models.course import Course  # noqa
from app.models.enrollment import Enrollment  # noqa
