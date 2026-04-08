"""Celery tasks for data synchronization."""

import logging
from app.tasks.celery_app import celery_app
from app.database import SyncSessionLocal
from app.sync.engine import run_sync
from app.sync.loaders.postgres_loader import clear_caches
from app.models.sync import SyncJob

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_tasks.run_sync_job", bind=True, max_retries=3)
def run_sync_job(self, sync_job_id: str, sync_type: str = "incremental"):
    """Run a single sync job (triggered manually or by scheduler)."""
    db = SyncSessionLocal()
    try:
        clear_caches()
        run_sync(db, sync_job_id, sync_type)
    except Exception as exc:
        logger.error(f"Sync job {sync_job_id} failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(name="app.tasks.sync_tasks.sync_all_active_jobs")
def sync_all_active_jobs():
    """Periodic task: run incremental sync for all active jobs."""
    db = SyncSessionLocal()
    try:
        jobs = db.query(SyncJob).filter(SyncJob.is_active == True).all()
        logger.info(f"Running incremental sync for {len(jobs)} active jobs")
        for job in jobs:
            try:
                clear_caches()
                run_sync(db, str(job.id), "incremental")
            except Exception as e:
                logger.error(f"Failed to sync job {job.id}: {e}")
    finally:
        db.close()
