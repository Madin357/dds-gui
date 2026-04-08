import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    connection_config_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON as text
    tables_to_sync_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    schedule_cron: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    institution: Mapped["Institution"] = relationship(back_populates="sync_jobs")
    runs: Mapped[list["SyncJobRun"]] = relationship(back_populates="sync_job")
    checkpoints: Mapped[list["SyncCheckpoint"]] = relationship(back_populates="sync_job")

    @property
    def connection_config(self) -> dict:
        return json.loads(self.connection_config_json) if self.connection_config_json else {}

    @property
    def tables_to_sync(self) -> list[str]:
        return json.loads(self.tables_to_sync_json) if self.tables_to_sync_json else []


class SyncJobRun(Base):
    __tablename__ = "sync_job_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    sync_job_id: Mapped[str] = mapped_column(ForeignKey("sync_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    sync_type: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    records_synced: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    sync_job: Mapped["SyncJob"] = relationship(back_populates="runs")


class SyncCheckpoint(Base):
    __tablename__ = "sync_checkpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    sync_job_id: Mapped[str] = mapped_column(ForeignKey("sync_jobs.id", ondelete="CASCADE"), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_record_id: Mapped[str | None] = mapped_column(String(100))
    row_count: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    sync_job: Mapped["SyncJob"] = relationship(back_populates="checkpoints")


class FieldMapping(Base):
    __tablename__ = "field_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_field: Mapped[str] = mapped_column(String(100), nullable=False)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_field: Mapped[str] = mapped_column(String(100), nullable=False)
    transform: Mapped[str | None] = mapped_column(String(50))
    transform_config: Mapped[str | None] = mapped_column(Text)  # JSON as text
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class IntegrationError(Base):
    __tablename__ = "integration_errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    sync_job_run_id: Mapped[str | None] = mapped_column(ForeignKey("sync_job_runs.id", ondelete="SET NULL"))
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    error_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_table: Mapped[str | None] = mapped_column(String(100))
    source_record_id: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    error_details: Mapped[str | None] = mapped_column(Text)  # JSON as text
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    institution_id: Mapped[str | None] = mapped_column(ForeignKey("institutions.id"), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[str | None] = mapped_column(String(36))
    details: Mapped[str | None] = mapped_column(Text)  # JSON as text
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


from app.models.institution import Institution  # noqa
