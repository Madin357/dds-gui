import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, desc

from app.api.deps import DB, CurrentUser
from app.models.sync import SyncJob, SyncJobRun, IntegrationError
from app.schemas.sync import SyncJobResponse, SyncJobRunResponse, SyncStatusResponse, TriggerSyncRequest

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/jobs", response_model=list[SyncJobResponse])
async def list_sync_jobs(user: CurrentUser, db: DB):
    query = select(SyncJob).where(SyncJob.institution_id == user.institution_id).order_by(SyncJob.created_at.desc())
    result = await db.execute(query)
    jobs = result.scalars().all()
    return [
        SyncJobResponse(
            id=j.id, name=j.name, source_type=j.source_type,
            is_active=j.is_active, schedule_cron=j.schedule_cron,
            tables_to_sync=j.tables_to_sync, created_at=j.created_at,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}/runs", response_model=list[SyncJobRunResponse])
async def list_sync_runs(job_id: str, user: CurrentUser, db: DB):
    # Verify job belongs to institution
    job_q = select(SyncJob).where(SyncJob.id == job_id, SyncJob.institution_id == user.institution_id)
    job = (await db.execute(job_q)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    query = select(SyncJobRun).where(SyncJobRun.sync_job_id == job_id).order_by(SyncJobRun.started_at.desc()).limit(50)
    result = await db.execute(query)
    return [SyncJobRunResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/jobs/{job_id}/trigger")
async def trigger_sync(job_id: str, req: TriggerSyncRequest, user: CurrentUser, db: DB):
    job_q = select(SyncJob).where(SyncJob.id == job_id, SyncJob.institution_id == user.institution_id)
    job = (await db.execute(job_q)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    # Run sync in a background thread
    import threading
    from app.database import SyncSessionLocal
    from app.sync.engine import run_sync
    from app.sync.loaders.postgres_loader import clear_caches

    def _run():
        sync_db = SyncSessionLocal()
        try:
            clear_caches()
            run_sync(sync_db, str(job_id), req.sync_type)
        finally:
            sync_db.close()

    threading.Thread(target=_run, daemon=True).start()
    return {"message": f"Sync triggered ({req.sync_type})"}


@router.get("/status", response_model=SyncStatusResponse)
async def sync_status(user: CurrentUser, db: DB):
    inst_id = user.institution_id

    total_jobs = (await db.execute(
        select(func.count()).where(SyncJob.institution_id == inst_id)
    )).scalar() or 0

    active_jobs = (await db.execute(
        select(func.count()).where(SyncJob.institution_id == inst_id, SyncJob.is_active == True)
    )).scalar() or 0

    # Last sync run
    last_run_q = (
        select(SyncJobRun)
        .join(SyncJob, SyncJob.id == SyncJobRun.sync_job_id)
        .where(SyncJob.institution_id == inst_id)
        .order_by(SyncJobRun.started_at.desc())
        .limit(1)
    )
    last_run = (await db.execute(last_run_q)).scalar_one_or_none()

    # Recent errors count (last 24h)
    from datetime import datetime, timedelta, timezone
    recent_errors = (await db.execute(
        select(func.count()).where(
            IntegrationError.institution_id == inst_id,
            IntegrationError.created_at >= datetime.now(timezone.utc) - timedelta(hours=24),
        )
    )).scalar() or 0

    return SyncStatusResponse(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        last_sync=SyncJobRunResponse.model_validate(last_run) if last_run else None,
        recent_errors=recent_errors,
    )


@router.get("/errors")
async def list_errors(user: CurrentUser, db: DB):
    query = (
        select(IntegrationError)
        .where(IntegrationError.institution_id == user.institution_id)
        .order_by(IntegrationError.created_at.desc())
        .limit(50)
    )
    result = await db.execute(query)
    return [
        {
            "id": str(e.id),
            "error_type": e.error_type,
            "source_table": e.source_table,
            "error_message": e.error_message,
            "resolved": e.resolved,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]
