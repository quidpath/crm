import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_service.settings.prod")
app = Celery("crm_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
