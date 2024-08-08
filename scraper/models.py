from typing import Collection, Iterable
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class Channel(models.Model):
    title = models.CharField(max_length=255)
    # The max length of youtube channel is 24
    channel_id = models.CharField(max_length=24, unique=True)

    def __str__(self):
        return self.title
    
    def get_channel_youtube_url(self):
        return f"https://www.youtube.com/channel/{self.channel_youtube_id}"
    
class Keyword(models.Model):
    keyword = models.CharField(max_length=50)

    def __str__(self):
        return self.keyword
    
class Group(models.Model):
    title = models.CharField(max_length=255)
    channels = models.ManyToManyField(Channel, related_name='groups')
    filter_from_date = models.DateField(default=now)
    keywords = models.ManyToManyField(Keyword, related_name='keywords')

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.keywords.count() > 3:
            raise ValidationError('A group can have a maximum of 3 keywords.')
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        self.full_clean()  # Call full_clean to ensure validation before saving 
