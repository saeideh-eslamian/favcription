from __future__ import absolute_import, unicode_literals
from django.conf import settings
import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "favcription.settings")
app = Celery("favcription")
app.config_from_object("django.conf:settings", namespace="CELERY")

# for find all shared task at all application
app.autodiscover_tasks(settings.INSTALLED_APPS)
