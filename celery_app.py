# projet/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicule.settings')

app = Celery('gestion_vehicule')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()