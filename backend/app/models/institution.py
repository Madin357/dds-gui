import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class InstitutionType(Base):
    __tablename__ = "institution_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    institutions: Mapped[list["Institution"]] = relationship(back_populates="type")


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("institution_types.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    logo_url: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    type: Mapped["InstitutionType"] = relationship(back_populates="institutions")
    users: Mapped[list["User"]] = relationship(back_populates="institution")
    programs: Mapped[list["Program"]] = relationship(back_populates="institution")
    students: Mapped[list["Student"]] = relationship(back_populates="institution")
    sync_jobs: Mapped[list["SyncJob"]] = relationship(back_populates="institution")


# Avoid circular import issues — these are resolved at runtime by SQLAlchemy
from app.models.user import User  # noqa: E402, F401
from app.models.program import Program  # noqa: E402, F401
from app.models.student import Student  # noqa: E402, F401
from app.models.sync import SyncJob  # noqa: E402, F401
