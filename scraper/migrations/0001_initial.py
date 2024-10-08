# Generated by Django 5.0.7 on 2024-08-04 13:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Channel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("channel_id", models.CharField(max_length=24, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Keyword",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keyword", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "filter_from_date",
                    models.DateField(default=django.utils.timezone.now),
                ),
                (
                    "channels",
                    models.ManyToManyField(related_name="groups", to="scraper.channel"),
                ),
                (
                    "keywords",
                    models.ManyToManyField(
                        related_name="keywords", to="scraper.keyword"
                    ),
                ),
            ],
        ),
    ]
