from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = 'Setup periodic tasks for the app'

    def handle(self, *args, **kwargs):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.DAYS,
        )

        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Send email with new videos every other day',
            task='scraper.tasks.send_email_to_users',
            defaults={'args': json.dumps([])},
        )

        self.stdout.write(self.style.SUCCESS('Periodic task created or already exists.'))