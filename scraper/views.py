from rest_framework import generics
from scraper.models import Channel, Group, Keyword
from scraper.serializers import ChannelSerializers, GroupSerializers, KeywordSerializers

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializers


class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializers