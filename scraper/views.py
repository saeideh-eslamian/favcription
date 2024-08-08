from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser

from .authentication import GoogleOAuth2Authentication
from .permissions import HasValidGoogleOAuth2Credentials
from .models import Channel, Group, Keyword
from .serializers import ChannelSerializers, GroupSerializers, KeywordSerializers


class ChannelView(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]
    
    def get(self, request, format=None):
        channels = Channel.objects.all()
        serializer = ChannelSerializers(channels, many=True)  # Corrected here
        return Response(serializer.data)

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializers
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]


class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializers
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]

class KeywordListCreateView(generics.ListCreateAPIView):   
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializers
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]


class KeywordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializers
    authentication_classes = [SessionAuthentication, GoogleOAuth2Authentication]
    permission_classes = [HasValidGoogleOAuth2Credentials]