import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Weather_reminder.settings')

app = Celery('Weather_reminder')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
