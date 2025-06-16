from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import logging

from scraper.api import YouTubeAPI
from scraper.models import Group, UserCredentials
import google.oauth2.credentials
from datetime import datetime
from social_django.models import UserSocialAuth
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


logger = logging.getLogger(__name__)



@shared_task
def fetch_and_send_youtube_videos():
    groups = Group.objects.all()
    print(f"Groups queryset type: {type(groups)}")
    for group in groups:
        print(f"Group instance: {group} (type: {type(group)})")
        print(group.title)

    for group in groups:
        try:
            # Get a user from the group who has Google OAuth
            user = group.owner
            if not user:
                continue

            try:
                social = UserSocialAuth.objects.get(user=user, provider='google-oauth2')
            except UserSocialAuth.DoesNotExist:
                logger.warning(f"No social auth for user {user.username}")
                continue

            extra_data = social.extra_data

            # Construct credentials from extra_data
            credentials = Credentials(
                token=extra_data.get('access_token'),
                refresh_token=extra_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
                client_secret=os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
                scopes=['https://www.googleapis.com/auth/youtube.readonly']
            )

            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Update stored token
                social.extra_data.update({
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'expires_at': credentials.expiry.timestamp() if credentials.expiry else None
                })
                social.save()

            # Use your YouTube API class with refreshed credentials
            youtube_api = YouTubeAPI(credentials)

            channels = group.channels.all()
            keywords = group.keywords.all()
            update_at = group.update_at

            all_new_videos = []
            for channel in channels:
                videos = youtube_api.get_new_videos(channel.channel_id, update_at)
                for video in videos:
                    if youtube_api.video_matches_keywords(video, keywords):
                        all_new_videos.append(video)

            if all_new_videos:
                video_links = "\n".join([v["url"] for v in all_new_videos])
                send_mail(
                    subject="New YouTube Videos Matching Your Interests",
                    message=f"Hi {user.username},\n\nHere are new videos:\n{video_links}",
                    from_email="chaaredan@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            logger.info(f"Processed group: {group.title}")

        except Exception as e:
            logger.error(f"Error processing group {group.id}: {e}")

    return "Done"


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


schedule, _ = IntervalSchedule.objects.get_or_create(every=2, period=IntervalSchedule.DAYS)

PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Fetch YouTube Videos Every Other Day',
    task='scraper.tasks.fetch_and_send_youtube_videos',
    defaults={'start_time': datetime.utcnow()},
)