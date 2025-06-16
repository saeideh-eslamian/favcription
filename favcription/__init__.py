from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app


#  to ensure Celery app is loaded when you start Django
__all__ = ('celery_app',)
