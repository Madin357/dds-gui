from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class SyncJobResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    is_active: bool
    schedule_cron: Optional[str] = None
    tables_to_sync: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SyncJobRunResponse(BaseModel):
    id: uuid.UUID
    sync_job_id: uuid.UUID
    status: str
    sync_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_synced: int = 0
    records_failed: int = 0
    error_summary: Optional[str] = None
    duration_ms: Optional[int] = None

    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    last_sync: Optional[SyncJobRunResponse] = None
    recent_errors: int = 0


class TriggerSyncRequest(BaseModel):
    sync_type: str = "incremental"  # 'full' or 'incremental'
