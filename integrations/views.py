# -*- coding: utf-8 -*-
"""Views for integrations. Most of these will just be ways to manually call tasks."""
# Standard Library

# 3rd-party
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader
from integrations.tasks import eventbrite_full_download


@staff_member_required
def get_eventbrite_event_ids(request):
    """Manually start the Eventbrite event ID download process."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    return HttpResponse("Complete", status=200)


@staff_member_required
def get_eventbrite_raw_event_data(request):
    """Manually start the Eventbrite event data download process."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    return HttpResponse("Complete", status=200)


@staff_member_required
def parse_eventbrite_data_into_events(request):
    """Manually start the Eventbrite event parsing process."""
    downloader = EventBriteEventParser()
    downloader.process_data()
    return HttpResponse("Complete", status=200)

@staff_member_required
def start_eventbrite_async_download(request):
    """Manually start the Eventbrite download process as a celery task."""
    eventbrite_full_download.delay()
    return HttpResponse("Started", status=200)
