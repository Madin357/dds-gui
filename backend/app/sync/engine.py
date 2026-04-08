"""
Sync engine orchestrator.
Handles both full and incremental syncs from institution source databases.

Flow: Source DB → Extract → Transform → Load (upsert) into platform DB
"""

import time
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.sync import SyncJob, SyncJobRun, SyncCheckpoint, IntegrationError
from app.sync.extractors.sqlite import SQLiteExtractor
from app.sync.transformers.base import transform_records
from app.sync.loaders.postgres_loader import upsert_records

logger = logging.getLogger(__name__)

# Table mapping: source table name → platform table + key fields
TABLE_CONFIG = {
    "programs": {
        "target_table": "programs",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "name": "name", "code": "code",
            "department": "department", "level": "level",
        },
    },
    "courses": {
        "target_table": "courses",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "program_id": "_program_source_id", "name": "name",
            "code": "code", "credits": "credits", "semester": "semester",
        },
    },
    "students": {
        "target_table": "students",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "student_code": "student_code",
            "first_name": "first_name", "last_name": "last_name",
            "email": "email", "date_of_birth": "date_of_birth",
            "gender": "gender", "enrollment_date": "enrollment_date",
            "current_gpa": "current_gpa", "current_semester": "current_semester",
            "status": "_status",
        },
    },
    "enrollments": {
        "target_table": "enrollments",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "student_id": "_student_source_id",
            "program_id": "_program_source_id", "status": "status",
            "enrolled_at": "enrolled_at", "completed_at": "completed_at",
            "dropped_at": "dropped_at", "drop_reason": "drop_reason",
            "final_gpa": "final_gpa",
        },
    },
    "attendance": {
        "target_table": "attendance_records",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "student_id": "_student_source_id",
            "course_id": "_course_source_id", "session_date": "session_date",
            "status": "status",
        },
    },
    "assessments": {
        "target_table": "assessments",
        "source_key": "id",
        "field_map": {
            "id": "source_id", "student_id": "_student_source_id",
            "course_id": "_course_source_id", "type": "type",
            "title": "title", "score": "score", "max_score": "max_score",
            "grade": "grade", "assessed_at": "assessed_at",
        },
    },
}

# Sync order matters (FK dependencies)
SYNC_ORDER = ["programs", "courses", "students", "enrollments", "attendance", "assessments"]


def run_sync(db_session: Session, sync_job_id: str, sync_type: str = "incremental"):
    """Execute a sync job (full or incremental)."""
    job = db_session.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
    if not job:
        logger.error(f"Sync job {sync_job_id} not found")
        return

    # Create run record
    run = SyncJobRun(
        sync_job_id=job.id,
        status="running",
        sync_type=sync_type,
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(run)
    db_session.commit()

    start_time = time.time()
    total_synced = 0
    total_failed = 0

    try:
        # Initialize extractor
        extractor = SQLiteExtractor(job.connection_config)

        tables_to_sync = [t for t in SYNC_ORDER if t in job.tables_to_sync]

        for table_name in tables_to_sync:
            config = TABLE_CONFIG.get(table_name)
            if not config:
                continue

            try:
                # Get checkpoint for incremental
                checkpoint = None
                if sync_type == "incremental":
                    checkpoint = (
                        db_session.query(SyncCheckpoint)
                        .filter(SyncCheckpoint.sync_job_id == job.id, SyncCheckpoint.table_name == table_name)
                        .first()
                    )

                last_synced = checkpoint.last_synced_at.isoformat() if checkpoint else None

                # Extract
                if sync_type == "full" or not last_synced:
                    records = extractor.extract_all(table_name)
                else:
                    records = extractor.extract_incremental(table_name, last_synced)

                if not records:
                    continue

                # Transform
                transformed = transform_records(
                    records, config["field_map"],
                    institution_id=str(job.institution_id),
                    target_table=config["target_table"],
                )

                # Load
                synced, failed = upsert_records(
                    db_session, config["target_table"], transformed,
                    institution_id=str(job.institution_id),
                    source_key="source_id",
                )
                total_synced += synced
                total_failed += failed

                # Update checkpoint
                now = datetime.now(timezone.utc)
                if checkpoint:
                    checkpoint.last_synced_at = now
                    checkpoint.row_count = synced
                else:
                    cp = SyncCheckpoint(
                        sync_job_id=job.id,
                        table_name=table_name,
                        last_synced_at=now,
                        row_count=synced,
                    )
                    db_session.add(cp)

                db_session.commit()
                logger.info(f"Synced {table_name}: {synced} records ({failed} failed)")

            except Exception as e:
                logger.error(f"Error syncing {table_name}: {e}")
                total_failed += 1
                error = IntegrationError(
                    sync_job_run_id=run.id,
                    institution_id=job.institution_id,
                    error_type="extraction" if "extract" in str(e).lower() else "load",
                    source_table=table_name,
                    error_message=str(e),
                )
                db_session.add(error)
                db_session.commit()

        # Finalize run
        duration_ms = int((time.time() - start_time) * 1000)
        run.status = "completed" if total_failed == 0 else "partial"
        run.completed_at = datetime.now(timezone.utc)
        run.records_synced = total_synced
        run.records_failed = total_failed
        run.duration_ms = duration_ms
        db_session.commit()

        logger.info(f"Sync completed: {total_synced} synced, {total_failed} failed, {duration_ms}ms")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error_summary = str(e)
        run.duration_ms = int((time.time() - start_time) * 1000)
        db_session.commit()
        raise
