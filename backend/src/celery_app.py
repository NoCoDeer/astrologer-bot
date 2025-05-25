from celery import Celery
from celery.schedules import crontab
from src.config import settings

# Create Celery app
celery_app = Celery(
    "astrologer_bot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "send-daily-horoscopes": {
        "task": "src.tasks.send_daily_horoscopes",
        "schedule": crontab(minute=0),  # Every hour
    },
    "reset-usage-counters": {
        "task": "src.tasks.reset_usage_counters",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-old-data": {
        "task": "src.tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
