# -*- coding: utf-8 -*-
"""Third party integrations models."""

# Standard Library
import uuid

# 3rd-party
from django.db import models


class EventBriteEventID(models.Model):
    """
    EventBrite event id's.

    This is stage 1 of the download process, get all the event ID's via web scraping.
    """

    event_id = models.BigIntegerField(primary_key=True)
    first_fetched = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True, blank=True)


class EventBriteRawEventData(models.Model):
    """EventBrite raw download data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.ForeignKey(EventBriteEventID, on_delete=models.CASCADE)
    data = models.JSONField()
