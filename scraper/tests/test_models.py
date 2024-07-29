from django.test import TestCase
from scraper.models import Channel


class ChannelTest(TestCase):
    def test_channel_creation(self):
        channel = Channel.objects.create(name="Test Channel", youtube_id="UC1234567890")
        self.assertEqual(channel.name, "Test Channel")
        self.assertEqual(channel.youtube_id, "UC1234567890")
