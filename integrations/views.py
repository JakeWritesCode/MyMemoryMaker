# -*- coding: utf-8 -*-
"""Views for integrations. Most of these will just be ways to manually call tasks."""
# Standard Library

# 3rd-party
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

# Project
from integrations.tasks import apply_rule_engine_to_unmoderated_results
from integrations.tasks import eventbrite_full_download
from integrations.tasks import get_all_eventbrite_event_ids
from integrations.tasks import get_all_eventbrite_raw_event_data
from integrations.tasks import parse_all_eventbrite_data_into_events


@staff_member_required
def get_eventbrite_event_ids(request):
    """Manually start the Eventbrite event ID download process."""
    get_all_eventbrite_event_ids.delay()
    return HttpResponse("Complete", status=200)


@staff_member_required
def get_eventbrite_raw_event_data(request):
    """Manually start the Eventbrite event data download process."""
    get_all_eventbrite_raw_event_data.delay()
    return HttpResponse("Complete", status=200)


@staff_member_required
def parse_eventbrite_data_into_events(request):
    """Manually start the Eventbrite event parsing process."""
    parse_all_eventbrite_data_into_events.delay()
    return HttpResponse("Complete", status=200)


@staff_member_required
def apply_ruleengine_to_unmoderated_results(request):
    """Apply the rule engine to unmoderated results."""
    apply_rule_engine_to_unmoderated_results.delay()
    return HttpResponse("Complete", status=200)


@staff_member_required
def start_eventbrite_async_download(request):
    """Manually start the Eventbrite download process as a celery task."""
    eventbrite_full_download.delay()
    return HttpResponse("Started", status=200)
