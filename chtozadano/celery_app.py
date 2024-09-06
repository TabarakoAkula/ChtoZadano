import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chtozadano.settings")
app = Celery("chtozadano")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
