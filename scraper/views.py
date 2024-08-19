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
        last_checked_date = group.filter_from_date

        new_videos = []
        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])
        youtube_api = YouTubeAPI(credentials)

        for channel in channels:
            # Fetch new videos for the channel after last_checked_date
            videos = youtube_api.get_new_videos(
                channel.channel_id, last_checked_date)

            # Filtering videos based on the updated video_matches_keywords
            for video in videos:
                if YouTubeAPI.video_matches_keywords(
                    youtube_api, video, keywords
                ):
                    if not Video.objects.filter(url=video['url']).exists():
                        data = {
                            'title': video['title'],
                            'url': video['url'],
                            'channel': channel.id,  # Use ID for ForeignKey
                            'group': group.id,  # Use ID for ForeignKey
                            'publish_date': video['published_at'],
                        }
                        video_serializer = VideoSerializer(data=data)
                        video_serializer.is_valid(raise_exception=True)
                        video_serializer.save()
                        new_videos.append(video_serializer.data)

        return Response(new_videos)


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
