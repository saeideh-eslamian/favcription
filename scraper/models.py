from django.db import models
from django.utils.timezone import now


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
    title = models.CharField(max_length=255, unique=True)
    channels = models.ManyToManyField(Channel, related_name='groups')
    filter_from_date = models.DateField(default=now)
    keywords = models.ManyToManyField(Keyword, related_name='keywords')

    def __str__(self):
        return self.title
        
    def update_last_checked(self):
        self.filter_from_date = now()
        self.save()


            
class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='videos')
    publish_date = models.DateTimeField()

    def __str__(self):
        return self.title