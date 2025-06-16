from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .authentication import GoogleOAuth2Authentication
from .permissions import HasValidGoogleOAuth2Credentials
from .models import Channel, Group, Keyword, Video
from .serializers import (
    ChannelSerializer,
    GroupSerializer,
    KeywordSerializer,
    VideoSerializer)
from .api import YouTubeAPI

import google.oauth2.credentials


class ChannelView(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request, format=None):
        channels = Channel.objects.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)


class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError:
            return JsonResponse(
                {"error": "A group with this title already exists."},
                status=400
            )


class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        keywords = group.keywords.all()
        channels = group.channels.all()
        update_at = group.update_at

        # Credentials from session
        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            request.session['credentials'] = credentials_to_dict(credentials)
        
        youtube_api = YouTubeAPI(credentials)

        new_videos = []

        for channel in channels:
            videos = youtube_api.get_new_videos(channel.channel_id, update_at)
            for video in videos:
                if youtube_api.video_matches_keywords(video, keywords):
                    if not Video.objects.filter(url=video['url']).exists():
                        data = {
                            'title': video['title'],
                            'url': video['url'],
                            'channel': channel.id,
                            'group': group.id,
                            'publish_date': video['published_at'],
                        }
                        video_serializer = VideoSerializer(data=data)
                        video_serializer.is_valid(raise_exception=True)
                        video_serializer.save()
                        new_videos.append(video_serializer.data)

        return Response(new_videos)


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

class KeywordListCreateView(generics.ListCreateAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]


class KeywordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]


class VideoListView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = [
        SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]
