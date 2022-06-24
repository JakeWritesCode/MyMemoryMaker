# -*- coding: utf-8 -*-
"""Integrations tasks."""
# Standard Library
from datetime import timedelta

# 3rd-party
from celery import shared_task
from django.utils import timezone

# Project
from integrations.constants import EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS
from integrations.constants import EVENTBRITE_EVENT_ID_URLS
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader
from integrations.models import EventBriteEventID
from integrations.models import EventBriteRawEventData
from search.models import Event, Activity, Place
from integrations.rule_engine import RuleEngine


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
        yield lst[i : i + n]


@shared_task()
def get_all_eventbrite_raw_event_data():
    """
    Get the API data for all EventBrite event ID's seen.

    The Eventbrite API is limited to 1k calls per hour, so we want to use this
    as effectively as possible.
    Priority queue:
    1. Most recently seen ID's with no data at all currently.
    2. Then oldest last downloaded.
    Max 500 at a time, to leave the other 500 calls per hour for the description call.
    """
    event_ids_no_data = EventBriteEventID.objects.exclude(
        event_id__in=EventBriteRawEventData.objects.all().values_list(
            "event_id__event_id", flat=True
        )
    )
    event_ids_no_data = event_ids_no_data.filter(
        last_seen__gt=timezone.now() - timedelta(hours=EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS)
    )
    event_ids_no_data = event_ids_no_data.order_by("-last_seen").values_list("event_id", flat=True)[
        :500
    ]

    if len(event_ids_no_data) < 500:
        extra_to_get = 500 - len(event_ids_no_data)
        extra_already_fetched = (
            EventBriteRawEventData.objects.filter(
                event_id__last_seen__gt=timezone.now()
                - timedelta(hours=EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS)
            )
            .order_by("last_fetched")
            .values_list("event_id__event_id")[:extra_to_get]
        )
        all_events = list(event_ids_no_data) + list(extra_already_fetched)

    for chunk in chunks(all_events, 100):
        get_eventbrite_raw_event_data.delay(chunk)


@shared_task(time_limit=1200)
def parse_eventbrite_data_into_events(event_ids):
    """Async task to turn eventbrite data into actual events."""
    downloader = EventBriteEventParser()
    downloader.process_data(event_ids)


@shared_task()
def parse_all_eventbrite_data_into_events():
    """
    Async task to turn all eventbrite data into actual events.

    Again we want to prioritise new events here and only re-do events after the fact.
    Max 500.
    """
    existing_events = Event.objects.filter(attributes__eventbrite_event_id__isnull=False)
    existing_event_ids = list(
        existing_events.values_list("attributes__eventbrite_event_id", flat=True)
    )
    unparsed_events = list(
        EventBriteRawEventData.objects.exclude(
            event_id__event_id__in=existing_event_ids
        ).values_list("event_id__event_id", flat=True)[:500]
    )
    if len(unparsed_events) < 500:
        parser = EventBriteEventParser()
        # We can do the last updated check here, to prevent duplication.
        for event in existing_events:
            raw_data = EventBriteRawEventData.objects.get(
                event_id__event_id=event.attributes["eventbrite_event_id"]
            )
            if parser.has_event_changed(event, raw_data):
                unparsed_events.append(raw_data.event_id.event_id)
            if len(unparsed_events) == 500:
                break

    for chunk in chunks(unparsed_events, 100):
        parse_eventbrite_data_into_events.delay(chunk)


@shared_task()
def apply_rule_engine_to_unmoderated_results():
    engine = RuleEngine()
    for entity_type in [Activity, Event, Place]:
        qs = entity_type.unmoderated.all()
        engine.apply_rules(qs)


@shared_task(time_limit=4800)
def eventbrite_full_download():
    """Perform a full download loop for EventBrite."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    downloader = EventBriteEventParser()
    downloader.process_data()
