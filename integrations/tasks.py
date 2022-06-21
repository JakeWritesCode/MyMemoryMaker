# -*- coding: utf-8 -*-
"""Integrations tasks."""
# 3rd-party
from datetime import timedelta

from celery import shared_task

# Project
from django.utils import timezone

from integrations.constants import EVENTBRITE_EVENT_ID_URLS, \
    EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader
from integrations.models import EventBriteEventID


@shared_task(time_limit=1200)
def get_eventbrite_event_ids_from_url(url):
    """Async tasks to get all EventIDs."""
    downloader = EventIDDownloader()
    downloader.get_event_ids(url)

@shared_task()
def get_all_eventbrite_event_ids():
    """Async tasks to get all EventIDs."""
    for url in EVENTBRITE_EVENT_ID_URLS:
        get_eventbrite_event_ids_from_url.delay(url)

@shared_task(time_limit=1200)
def get_eventbrite_raw_event_data(event_ids):
    """Async task to get raw data for found events."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events(event_ids)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@shared_task()
def get_all_eventbrite_raw_event_data():
    """Async task to get raw data for found events."""
    all_events = EventBriteEventID.objects.filter(
            last_seen__gt=timezone.now() - timedelta(hours=EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS),
        ).values_list("id", flat=True)
    all_events = list(all_events)
    for chunk in chunks(all_events, 100):
        get_eventbrite_raw_event_data.delay(chunk)


@shared_task(time_limit=1200)
def parse_eventbrite_data_into_events():
    """Async task to turn eventbrite data into actual events."""
    downloader = EventBriteEventParser()
    downloader.process_data()


@shared_task(time_limit=4800)
def eventbrite_full_download():
    """Perform a full download loop for EventBrite."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    downloader = EventBriteEventParser()
    downloader.process_data()
