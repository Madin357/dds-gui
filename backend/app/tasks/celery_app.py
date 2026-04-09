import os

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "eduscope_tasks",
    broker=os.environ.get("REDIS_URL", settings.REDIS_URL),
    backend=os.environ.get("REDIS_URL", settings.REDIS_URL),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Baku",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    "sync-all-active-jobs": {
        "task": "app.tasks.sync_tasks.sync_all_active_jobs",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "recompute-analytics": {
        "task": "app.tasks.analytics_tasks.recompute_all_analytics",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}
