# Generated by Django 4.0.4 on 2022-06-19 06:56

# 3rd-party
from django.db import migrations
from django.db import models

# Project
import search.models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0006_alter_activity_source_id_alter_event_source_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="searchimage",
            name="uploaded_image",
            field=models.ImageField(null=True, upload_to=search.models.search_image_upload_path),
        ),
    ]
