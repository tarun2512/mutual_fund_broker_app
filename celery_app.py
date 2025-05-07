from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()
print(os.environ.get("REDIS_URI"))
celery_app = Celery(
    "my_tasks",
    broker=f'{os.environ.get("REDIS_URI")}/10',  # Redis broker
    backend=f'{os.environ.get("REDIS_URI")}/11',  # Redis backend (optional)
)

celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True
