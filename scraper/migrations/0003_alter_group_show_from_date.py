# Generated by Django 5.0.7 on 2024-07-30 08:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scraper", "0002_keyword_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="show_from_date",
            field=models.DateField(
                default=datetime.datetime(
                    2024, 7, 30, 8, 55, 7, 767267, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
