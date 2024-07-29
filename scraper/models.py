from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=255)
    # The max length of youtube channel is 24
    youtube_id = models.CharField(max_length=24, unique=True)

    def __str__(self):
        return self.name
    
    def get_channel_youtube_url(self):
        return f"https://www.youtube.com/@{self.channel_youtube_id}"