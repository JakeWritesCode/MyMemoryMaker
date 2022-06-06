# Generated by Django 4.0.4 on 2022-06-06 07:19

# 3rd-party
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0004_activity_last_updated_event_external_link_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="source_type",
            field=models.CharField(
                choices=[("manually_added", "manually_added"), ("eventbrite", "eventbrite")],
                max_length=256,
                verbose_name="Source of entity.",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="source_type",
            field=models.CharField(
                choices=[("manually_added", "manually_added"), ("eventbrite", "eventbrite")],
                max_length=256,
                verbose_name="Source of entity.",
            ),
        ),
        migrations.AlterField(
            model_name="place",
            name="source_type",
            field=models.CharField(
                choices=[("manually_added", "manually_added"), ("eventbrite", "eventbrite")],
                max_length=256,
                verbose_name="Source of entity.",
            ),
        ),
    ]
