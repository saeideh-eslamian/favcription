from django.shortcuts import redirect
from django.urls import reverse
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

from .authentication import GoogleOAuth2Authentication
from .permissions import HasValidGoogleOAuth2Credentials
from scraper.models import Channel

# Google imports
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.discovery import build

import logging

logger = logging.getLogger(__name__)

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


class AuthorizeView(APIView):
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES
        )
        flow.redirect_uri = request.build_absolute_uri(
            reverse("oauth2callback"))
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        request.session["state"] = state
        request.session.save()

        return redirect(authorization_url)


class OAuth2CallbackView(APIView):
    """Handles the OAuth2 callback and token exchange"""

    def get(self, request):
        state = request.session["state"]
        if state is None:
            return Response(
                "State is missing in session",
                status=status.HTTP_400_BAD_REQUEST
            )

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = request.build_absolute_uri(
            reverse("oauth2callback"))

        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        request.session["credentials"] = self.credentials_to_dict(
            credentials)
        return redirect(reverse("youtube-subscriptions"))

    def credentials_to_dict(self, credentials) -> dict:
        """
        Converts google.oauth2.credentials.Credentials object into a dictionary
        to store in the session.
        This allows the credentials to be easily saved and retrieved
        """
        return {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }


class YouTubeSubscriptionsView(APIView):
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request, *args, **kwargs):
        if "credentials" not in request.session:
            return Response(
                {"error": "Google account not authorized."},
                status=400
                )

        token = request.session["credentials"]["token"]
        subscriptions = self.get_subscriptions(token)

        for sub in subscriptions:
            Channel.objects.get_or_create(
                title=sub["title"],
                channel_id=sub["channel_id"],
            )
        return Response({"message": "Subscriptions updated."})

    def get_subscriptions(self, token):
        credentials = google.oauth2.credentials.Credentials(token=token)
        youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials
        )

        subscriptions = []
        request = youtube.subscriptions().list(part="snippet", mine=True, maxResults=50)

        while request:
            response = request.execute()
            for item in response.get("items", []):
                subscriptions.append({
                    "title": item["snippet"]["title"],
                    "channel_id": item["snippet"]["resourceId"]["channelId"],
                })

            # Check if there is a next page
            request = youtube.subscriptions().list_next(request, response)
   
        return subscriptions


class RefreshTokenView(APIView):
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request):
        if "credentials" not in request.session:
            return Response({"error": "No credentials in session"}, status=400)

        credentials = google.oauth2.credentials.Credentials(
            **request.session["credentials"]
        )

        # Refresh the token
        if credentials.expired:
            request.session["credentials"] = self.credentials_to_dict(
                credentials.refresh()
            )

        return Response({"message": "Token refreshed"})


class RevokeView(APIView):
    """Revokes the OAuth2 credentials"""

    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request):
        if "credentials" not in request.session:
            msg = "You need to authorize before \
                testing the code to revoke credentials."
            return Response(
                msg,
                status=status.HTTP_400_BAD_REQUEST,
            )

        credentials = google.oauth2.credentials.Credentials(
            **request.session["credentials"]
        )

        revoke = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": credentials.token},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        if revoke.status_code == 200:
            del request.session["credentials"]
            return Response("Credentials successfully revoked.")
        else:
            return Response(
                "An error occurred while revoking credentials",
                status=status.HTTP_400_BAD_REQUEST,
            )


class YouTubeAPI:
    def __init__(self, credentials):
        self.youtube = build(API_SERVICE_NAME, API_VERSION,
                             credentials=credentials)

    def get_new_videos(self, channel_id, last_checked_date):
        """Fetch new videos from YouTube channel after the last checked date"""
        published_after = last_checked_date.isoformat() + "T00:00:00Z"
        search_request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            publishedAfter=published_after,
            maxResults=10,
            order="date",
        )
        try:
            search_response = search_request.execute()
            logger.debug(f"API response: {search_response}")
        except Exception as e:
            logger.error(f"API error: {e}")
            return []

        videos = []
        for item in search_response.get("items", []):
            description = item["snippet"].get("description", "")
            hashtags = self.extract_hashtags_from_description(description)

            video = {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "hashtags": hashtags,
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "url":
                f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            }
            logger.info(
                f"Fetched video: {video['title']} with ID: {video['video_id']}"
            )
            videos.append(video)

        logger.info(f"Total videos fetched: {len(videos)}")
        return videos

    def extract_hashtags_from_description(self, description):
        """Extract hashtags from the video description."""
        hashtags = []
        words = description.split()
        for word in words:
            if word.startswith("#"):
                hashtags.append(word)
        return hashtags

    def video_matches_keywords(self, video, keywords):
        """Check if a video title or hastags matches any of the keywords."""
        title = video["title"].lower()
        hashtags = [tag.lower() for tag in video["hashtags"]]

        for keyword in keywords:
            keyword_lower = keyword.keyword.lower()
            if keyword_lower in title or keyword_lower in hashtags:
                return True
        return False
