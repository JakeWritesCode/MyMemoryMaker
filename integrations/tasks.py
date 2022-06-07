# -*- coding: utf-8 -*-
"""Integrations tasks."""
# 3rd-party
from celery import shared_task

# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader


@shared_task
def get_eventbrite_event_ids():
    """Async tasks to get all EventIDs."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()


@shared_task(time_limit=1200)
def get_eventbrite_raw_event_data():
    """Async task to get raw data for found events."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()


@shared_task(time_limit=1200)
def parse_eventbrite_data_into_events():
    """Async task to turn eventbrite data into actual events."""
    downloader = EventBriteEventParser()
    downloader.process_data()


@shared_task(time_limit=2400)
def eventbrite_full_download():
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    downloader = EventBriteEventParser()
    downloader.process_data()
