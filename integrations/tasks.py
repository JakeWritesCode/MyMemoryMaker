# -*- coding: utf-8 -*-
"""Integrations tasks."""
# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader


def get_eventbrite_event_ids():
    """Async tasks to get all EventIDs."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()


def get_eventbrite_raw_event_data():
    """Async task to get raw data for found events."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()


def parse_eventbrite_data_into_events():
    """Async task to turn eventbrite data into actual events."""
    downloader = EventBriteEventParser()
    downloader.process_data()
