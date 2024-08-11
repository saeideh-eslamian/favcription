from rest_framework import serializers
from scraper.models import Channel, Group, Keyword, Video
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    def validate_keywords(self, value):
        # Perform validation: Ensure no more than 3 keywords are added
        if len(value) > 3:
            raise ValidationError('A group can have a maximum of 3 keywords.')
        return value
    
    class Meta:
        model = Group
        fields = "__all__"


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__" 

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"                      