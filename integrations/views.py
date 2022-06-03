# -*- coding: utf-8 -*-
"""Views for integrations. Most of these will just be ways to manually call tasks."""
# 3rd-party
from django.http import HttpResponse

# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader


def get_eventbrite_event_ids(request):
    """Manually start the Eventbrite event ID download process."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    return HttpResponse("Complete", status=200)


def get_eventbrite_raw_event_data(request):
    """Manually start the Eventbrite event data download process."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    return HttpResponse("Complete", status=200)


def parse_eventbrite_data_into_events(request):
    """Manually start the Eventbrite event parsing process."""
    downloader = EventBriteEventParser()
    downloader.process_data()
    return HttpResponse("Complete", status=200)
