from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import logging


logger = logging.getLogger(__name__)


# Create schedule for send emails
def setup_interval_schedule():
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,  # desired interval
        period=IntervalSchedule.DAYS,
    )
    return schedule


@shared_task
def send_email_to_users():
    try:
        users = User.objects.all()
        for user in users:
            send_mail(
                subject="Subject: Your Favorite YouTube Video",
                message=f"Hi {user.username}, this is an automatic email.",
                from_email="chaaredan@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
        logger.info("Emails successfully sent to users.")
    except Exception as e:
        logger.error(f"Error sending emails: {e}")
        raise


# Task setup helper
def setup_periodic_task():
    schedule = setup_interval_schedule()
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Send email to users every day",
        task="scraper.tasks.send_email_to_users",
    )
