from rest_framework import serializers
from scraper.models import Channel, Group, Keyword

class ChannelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Channel
        feilds = "__all__"

class GroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        feilds = "__all__"

class KeywordSerializers(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        feilds = "__all__"                