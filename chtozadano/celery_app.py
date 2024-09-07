import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chtozadano.settings")

app = Celery("chtozadano")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "delete-old-homework": {
        "task": "homework.utils.celery_delete_old_homework",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
}

app.conf.timezone = "Europe/Moscow"
