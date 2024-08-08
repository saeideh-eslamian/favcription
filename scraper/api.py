
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

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


class AuthorizeView(APIView):
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = request.build_absolute_uri(
            reverse('oauth2callback'))
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',

        )

        request.session['state'] = state
        request.session.save()

        return redirect(authorization_url)


class OAuth2CallbackView(APIView):
    """Handles the OAuth2 callback and token exchange"""
    def get(self, request):
        state = request.session['state']
        if state is None:
            return Response("State is missing in session", status=status.HTTP_400_BAD_REQUEST)
        
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
        flow.redirect_uri = request.build_absolute_uri(
            reverse('oauth2callback'))

        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        request.session['credentials'] = self.credentials_to_dict(credentials)
        return redirect(reverse('youtube-subscriptions'))
    
    def credentials_to_dict(self, credentials) -> dict:
        """
        Converts google.oauth2.credentials.Credentials object into a dictionary to store in the session.
        This allows the credentials to be easily saved and retrieved
        """
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
                }


class YouTubeSubscriptionsView(APIView):
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request, *args, **kwargs):
        if 'credentials' not in request.session:
            return Response({"error": "Google account not authorized."}, status=400)

        token = request.session['credentials']['token']
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
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        request = youtube.subscriptions().list(part="snippet", mine=True)
        response = request.execute()
        subscriptions = []
        for item in response.get("items", []):
            subscriptions.append({
                "title": item["snippet"]["title"],
                "channel_id": item["snippet"]["resourceId"]["channelId"]
            })
        return subscriptions
    
class RefreshTokenView(APIView):
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]
    def get(self, request):
        if 'credentials' not in request.session:
            return Response({"error": "No credentials in session"}, status=400)

        credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
        
        # Refresh the token
        if credentials.expired:
            request.session['credentials'] = self.credentials_to_dict(credentials.refresh())

        return Response({"message": "Token refreshed"})
    
class RevokeView(APIView):
    """Revokes the OAuth2 credentials"""
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request):
        if 'credentials' not in request.session:
            return Response('You need to authorize before testing the code to revoke credentials.', status=status.HTTP_400_BAD_REQUEST)

        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])

        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': credentials.token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})

        if revoke.status_code == 200:
            del request.session['credentials']
            return Response('Credentials successfully revoked.')
        else:
            return Response('An error occurred while revoking credentials', status=status.HTTP_400_BAD_REQUEST)   