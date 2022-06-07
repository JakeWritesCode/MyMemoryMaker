# -*- coding: utf-8 -*-
"""Integrations tasks."""
# 3rd-party
from celery import shared_task

# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader


@shared_task
def get_eventbrite_event_ids(trigger_get_data=False):
    """Async tasks to get all EventIDs."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    if trigger_get_data:
        get_eventbrite_raw_event_data.delay(trigger_parse_data=True)


@shared_task(time_limit=1200)
def get_eventbrite_raw_event_data(trigger_parse_data=False):
    """Async task to get raw data for found events."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    if trigger_parse_data:
        parse_eventbrite_data_into_events.delay()


@shared_task(time_limit=1200)
def parse_eventbrite_data_into_events():
    """Async task to turn eventbrite data into actual events."""
    downloader = EventBriteEventParser()
    downloader.process_data()


@shared_task
def eventbrite_full_download():
    get_eventbrite_event_ids.delay(trigger_get_data=True)
