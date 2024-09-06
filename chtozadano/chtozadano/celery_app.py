import os

from celery import Celery
from django.conf import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "chtozadano.settings"

app = Celery("chtozadano")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = settings.CELERY_BROKER_URL

app.autodiscover_tasks()
