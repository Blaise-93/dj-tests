import os

from decouple import config
from celery import Celery

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", config("DJANGO_SETTINGS_MODULE"))
os.environ.setdefault(config('DJANGO_SETTINGS_MODULE'),
                      'pharmaceuticals.settings',)
app = Celery("pharmaceuticals")
app.config_from_object("django.pharmaceuticals:settings", namespace="CELERY")
app.autodiscover_tasks()
