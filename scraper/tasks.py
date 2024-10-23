from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule


# Create the interval schedule for every 2 days
schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.DAYS,
)


@shared_task
def send_email_to_users():
    users = User.objects.all()
    for user in users:
        send_mail(
            'Subject: your favorite Youtube video',
            'This is an automatic email sent every 1 days.',
            'chaaredan@gmail.com',
            [user.email],
            fail_silently=False,
        )
    #
    # for Debug TODO change to pass
    return "Done"


# Create the periodic task
PeriodicTask.objects.create(
    interval=schedule,
    name='Send email to users every 3 days',
    task='scraper.tasks.send_email_to_users',
)
