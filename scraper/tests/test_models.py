from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from scraper.models import Channel, Group, Keyword

class ChannelModelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(title="Test Channel", channel_id="UC1234567890")

    def test_channel_creation(self):
        self.assertEqual(self.channel.title, "Test Channel")
        self.assertEqual(self.channel.channel_id, "UC1234567890")

    def test_channel_str(self):
        self.assertEqual(str(self.channel), "Test Channel")

class KeywordModelTest(TestCase):

    def setUp(self):
        self.keyword = Keyword.objects.create(keyword="test")

    def test_keyword_creation(self):
        self.assertEqual(self.keyword.keyword, "test")
        self.assertEqual(str(self.keyword), "test")        


class GroupModelTest(TestCase):

    def setUp(self):
        self.channel1 = Channel.objects.create(title="Test Channel 1", channel_id="UC1234567890")
        self.channel2 = Channel.objects.create(title="Test Channel 2", channel_id="UC0987654321")
        self.keyword1 = Keyword.objects.create(keyword="test1")
        self.keyword2 = Keyword.objects.create(keyword="test2")
        self.keyword3 = Keyword.objects.create(keyword="test3")
        self.keyword4 = Keyword.objects.create(keyword="test4")
        self.group = Group.objects.create(title="Test Group", filter_from_date=timezone.now())
        
        # Now that the group is saved, you can set the many-to-many fields
        self.group.channels.set([self.channel1, self.channel2])
        self.group.keywords.set([self.keyword1, self.keyword2, self.keyword3])

    def test_group_creation(self):
        self.assertEqual(self.group.title, "Test Group")
        self.assertEqual(self.group.channels.count(), 2)

    def test_group_str(self):
        self.assertEqual(str(self.group), "Test Group")

    def test_group_creation_with_valid_keywords(self):
        self.group.keywords.set([self.keyword1, self.keyword2, self.keyword3])

        try:
            self.group.full_clean()
        except ValidationError:
            self.fail("group.full_clean() raised ValidationError unexpectedly!")

        self.assertEqual(self.group.keywords.count(), 3)
        self.assertIn(self.keyword1, self.group.keywords.all())
        self.assertIn(self.keyword2, self.group.keywords.all())
        self.assertIn(self.keyword3, self.group.keywords.all()) 

    # def test_group_creation_with_more_than_three_keywords(self):
    #     self.group.channels.add(self.channel1)
    #     self.group.keywords.set([self.keyword1, self.keyword2, self.keyword3, self.keyword4])

    #     with self.assertRaises(ValidationError):
    #         self.group.full_clean()