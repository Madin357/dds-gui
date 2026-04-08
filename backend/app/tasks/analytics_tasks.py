"""Celery tasks for analytics computation."""

import logging
from app.tasks.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.institution import Institution
from app.analytics.aggregator import compute_student_scores, compute_program_scores, compute_institution_kpis

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.analytics_tasks.recompute_all_analytics")
def recompute_all_analytics():
    """Periodic task: recompute analytics for all institutions."""
    db = SyncSessionLocal()
    try:
        institutions = db.query(Institution).filter(Institution.is_active == True).all()
        for inst in institutions:
            try:
                compute_analytics_for_institution(str(inst.id))
            except Exception as e:
                logger.error(f"Failed to compute analytics for {inst.id}: {e}")
    finally:
        db.close()


@celery_app.task(name="app.tasks.analytics_tasks.compute_analytics_for_institution")
def compute_analytics_for_institution(institution_id: str):
    """Compute all analytics for a single institution."""
    db = SyncSessionLocal()
    try:
        compute_student_scores(db, institution_id)
        compute_program_scores(db, institution_id)
        compute_institution_kpis(db, institution_id)
        logger.info(f"All analytics computed for {institution_id}")
    finally:
        db.close()
