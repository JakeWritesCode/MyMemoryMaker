# Generated by Django 4.0.4 on 2022-06-06 07:19

# 3rd-party
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0002_eventbriteraweventdata_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventbriteeventid",
            name="first_fetched",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="eventbriteeventid",
            name="last_seen",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]