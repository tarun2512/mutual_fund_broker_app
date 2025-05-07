from celery.schedules import crontab
from celery_app import celery_app

celery_app.conf.beat_schedule = {
    "run-my-hourly-function": {
        "task": "task.my_hourly_function",
        "schedule": crontab(minute=0, hour="*"),  # every hour
    },
}
