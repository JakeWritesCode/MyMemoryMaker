# -*- coding: utf-8 -*-
"""EventBrite API integration."""
# Standard Library
import json
import logging
import re
from datetime import datetime
from datetime import timedelta
from http.client import OK

# 3rd-party
import bleach
import googlemaps
import pytz
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.db import IntegrityError
from django.utils import timezone
from googlemaps.exceptions import TransportError
from pytz import UTC

# Project
from integrations.constants import BLEACH_ALLOWED_ATTRIBUTES
from integrations.constants import BLEACH_ALLOWED_TAGS
from integrations.constants import EVENTBRITE_CATEGORY_MAPPING
from integrations.constants import EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS
from integrations.exceptions import APIError
from integrations.models import EventBriteEventID
from integrations.models import EventBriteRawEventData
from integrations.utils import http_request_with_backoff
from search.constants import SEARCH_ENTITY_SOURCES
from search.models import Event
from search.models import Place
from search.models import SearchImage
from users.models import CustomUser


def get_or_create_api_user():
    """We need a user to 'upload' the data. Create a fake user if one doesn't exist for the api."""
    user, _ = CustomUser.objects.get_or_create(
        email="integrations@mymemorymaker.com",
        first_name="MyMemoryMaker",
        last_name="Integrations API",
    )
    return user


class EventIDDownloader:
    """
    Stage 1 of the download process.

    EventBrite have closed off access to their event lists API so fetch the same data with a bit
    of light web scraping.
    """

    def _fetch_page_content(self, url, page_id: int):
        """Perform a GET request for that page's events."""
        url = f"{url}?page={page_id}"
        response = http_request_with_backoff("get", url)
        if response.status_code != OK:
            raise APIError(f"The page {url} did not return the correct status, status {response.status_code}.")

        data = str(response.content)
        return data

    def _check_for_results(self, page_content):
        """
        Check to see if the page has run out of options.

        Currently, the eventbrite web page shows 1-X results at the bottom, the 1 is the page
        number but the X is actually the number of events, not pages. Check for the text
        'Nothing matched your search, but you might like these options." to denote end of listings.
        """
        if "Nothing matched your search, but you might like these options." in page_content:
            return False
        return True

    def _get_event_ids_from_page(self, page_content: str):
        """Get event id's by web scraping."""
        event_ids = []
        links = re.findall(
            'href="https:\/\/www\.eventbrite\.com\/e\/(.*?)"',  # noqa: W605
            page_content,
        )
        links += re.findall(
            'href="https:\/\/www\.eventbrite\.co.uk\/e\/(.*?)"',  # noqa: W605
            page_content,
        )

        for link in links:
            event_id = link.split("?")[0]
            event_id = event_id.split("-")[-1]
            event_ids.append(event_id)
        event_ids = list(set(event_ids))

        return event_ids

    def get_event_ids(self, base_url):
        """Get and update all event ID's from the EventBrite site."""
        logging.info(f"Beginning EventBrite event ID download from {base_url} @ {timezone.now()}")

        for page_number in range(1, 500):
            try:
                page_content = self._fetch_page_content(base_url, page_number)
            except APIError:
                continue

            if not self._check_for_results(page_content):
                logging.info(
                    f"EventBrite event ID downloader ran out of pages on page {page_number}",
                )
                return

            event_ids = self._get_event_ids_from_page(page_content)
            for event_id in event_ids:
                event, _ = EventBriteEventID.objects.get_or_create(event_id=event_id)
                event.last_seen = timezone.now()
                event.save()
            logging.info(f"EventBrite event ID downloader completed downloading page {page_number}")

        logging.info(f"Completed EventBrite event ID download @ {timezone.now()}")
        return True


class EventRawDataDownloader:
    """Download the raw data from the API endpoint."""

    def _get_event_data(self, event_id):
        """Get an event from the API."""
        url = (
            f"https://www.eventbriteapi.com/v3/events/{event_id}/"
            f"?expand=category,subcategory,venue,format,listing_properties,ticket_availability"
            f"&token={settings.EVENTBRITE_API_KEY}"
        )
        response = http_request_with_backoff("get", url)
        if response.status_code != OK:
            raise APIError(
                f"The API did not return a correct response. "
                f"{response.status_code}, {response.content}",
            )
        return json.loads(response.content)

    def get_recently_seen_events(self, event_ids):
        """Get all the recently seen events."""
        for event_id in event_ids:
            try:
                event_id_obj = EventBriteEventID.objects.get(event_id=event_id)
                try:
                    raw_data = EventBriteRawEventData.objects.get(event_id=event_id_obj)
                except EventBriteRawEventData.DoesNotExist:
                    raw_data = EventBriteRawEventData(event_id=event_id_obj)
                event_data = self._get_event_data(event_id)
                raw_data.data = event_data
                raw_data.save()
            except APIError:
                continue


class EventBriteEventParser:
    """Turn Raw EventBrite data into events."""

    def __init__(self):
        """Create a gmaps client."""
        self.gmaps_client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def _has_event_changed(self, event: Event, raw_data: EventBriteRawEventData):
        """Has the event changed compared to the last time we looked."""
        try:
            last_updated = datetime.strptime(raw_data.data["changed"], "%Y-%m-%dT%H:%M:%SZ")
        except TypeError:  # Event has not changed date.
            if not event.headline:
                return True
            return False
        last_updated = timezone.make_aware(last_updated, timezone=UTC)
        if last_updated > event.last_updated:
            return True
        return False

    def _parse_datetime(self, dt, tz):
        output_dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        output_tz = pytz.timezone(tz)
        return timezone.make_aware(output_dt, output_tz)

    def _determine_filters(self, raw_data: EventBriteRawEventData):
        """Figure out which filters apply based on the filter mapping."""
        filters = {}

        for _, cat_data in EVENTBRITE_CATEGORY_MAPPING.items():
            if raw_data.data["category_id"]:
                if cat_data["id"] == raw_data.data["category_id"]:
                    filters |= {our_filter: True for our_filter in cat_data["our_filters"]}

            if raw_data.data["subcategory_id"]:
                for subcat_data in cat_data["subcategories"]:
                    if subcat_data["id"] == raw_data.data["subcategory_id"]:
                        filters |= {our_filter: True for our_filter in subcat_data["our_filters"]}

        return filters

    def _build_photo_from_gmaps_data(self, image: SearchImage, gmaps_data: dict, place: Place):
        """
        Google maps rotates its images so we can't just us the URL. We'll need to download.

        Save the emage as a SearchImage.
        """
        img_data = self.gmaps_client.places_photo(gmaps_data["photo_reference"], max_width=10000)
        temp_image = NamedTemporaryFile()
        for block in img_data:
            # If no more file then stop
            if not block:
                break
            # Write image block to temporary file
            temp_image.write(block)
        image.uploaded_by = get_or_create_api_user()
        image.alt_text = place.headline
        image.uploaded_image.save(f"{gmaps_data['photo_reference']}.jpeg", temp_image)
        image.save()

    def _build_place(self, event: Event, raw_data: EventBriteRawEventData):
        """
        Build the associated place using the Google maps API.

        This is not guaranteed to work 100% of the time, but we'll follow this process:
        1. Get the venue name and try and find it using the Places API.
        2. We're provided with the lat and long, so check that we've got the right place.
        """
        search_point = (
            raw_data.data["venue"]["address"]["latitude"],
            raw_data.data["venue"]["address"]["longitude"],
        )
        radius = 1000  # Meters, I think...
        gmaps_places = self.gmaps_client.places(
            raw_data.data["venue"]["name"],
            location=search_point,
            radius=radius,
        )
        if len(gmaps_places["results"]) == 0:
            raise ValueError(
                f"Unable to find a matching Google Maps place for {raw_data.data['venue']['name']}",
            )

        gmaps_place = gmaps_places["results"][0]
        # Do we already have a place? If so, use it but update it anyway.
        existing_places = Place.objects.filter(google_maps_place_id=gmaps_place["place_id"])
        if len(existing_places) > 0:
            mmm_place = existing_places[0]
            image = mmm_place.images.first()
            if not image:
                image = SearchImage()
            new_place = False
        else:
            mmm_place = Place()
            image = SearchImage()
            new_place = True

        # Update place data
        if new_place:
            mmm_place.headline = gmaps_place["name"]
            mmm_place.description = gmaps_place["name"]
            mmm_place.price_lower = event.price_lower
            mmm_place.price_upper = event.price_upper
            mmm_place.duration_lower = event.duration_lower
            mmm_place.duration_upper = event.duration_upper
            mmm_place.people_lower = event.people_lower
            mmm_place.people_upper = event.people_upper
            mmm_place.source_type = SEARCH_ENTITY_SOURCES[1]
            mmm_place.source_id = raw_data.event_id.event_id
            mmm_place.google_maps_place_id = gmaps_place["place_id"]
            mmm_place.location_lat = gmaps_place["geometry"]["location"]["lat"]
            mmm_place.location_long = gmaps_place["geometry"]["location"]["lng"]
            mmm_place.created_by = get_or_create_api_user()
            if not mmm_place.attributes:
                mmm_place.attributes = {}
        mmm_place.attributes = (
            mmm_place.attributes
            | {
                "google_maps_data": {
                    "rating": gmaps_place.get("rating", None),
                    "address": gmaps_place["formatted_address"],
                },
            }
            | event.attributes
        )
        mmm_place.save()
        if len(gmaps_place["photos"]) > 0:
            self._build_photo_from_gmaps_data(image, gmaps_place["photos"][0], mmm_place)
            mmm_place.images.add(image)
        return mmm_place

    def _update_description(self, event, event_id):
        """The description is a separate API call. This is untrusted HTML, so bleach it."""
        url = (
            f"https://www.eventbriteapi.com/v3/events/{event_id}/"
            f"description/?token={settings.EVENTBRITE_API_KEY}"
        )
        response = http_request_with_backoff("get", url)
        if response.status_code != OK:
            raise ValueError(
                f"Unable to update description. Response code="
                f"{response.status_code}, error={response.content}",
            )
        data = json.loads(response.content)
        description = data["description"]
        description = bleach.clean(
            description,
            tags=BLEACH_ALLOWED_TAGS,
            attributes=BLEACH_ALLOWED_ATTRIBUTES,
        )
        event.description = description

    def _populate_event(self, event: Event, raw_data: EventBriteRawEventData):
        """Populate the event with the latest data from the API."""
        event.last_updated = timezone.now()
        event.approved_by = None
        event.approval_timestamp = None
        event.created_by = get_or_create_api_user()

        # Update the stuff that we need, or else fail with log.
        try:
            event.headline = raw_data.data["name"]["text"]
            event.price_lower = float(
                raw_data.data["ticket_availability"]["minimum_ticket_price"]["major_value"],
            )
            event.price_upper = float(
                raw_data.data["ticket_availability"]["maximum_ticket_price"]["major_value"],
            )
            event_start = self._parse_datetime(
                raw_data.data["start"]["utc"],
                raw_data.data["start"]["timezone"],
            )
            event_end = self._parse_datetime(
                raw_data.data["end"]["utc"],
                raw_data.data["end"]["timezone"],
            )
            event.duration_lower = ((event_end - event_start).total_seconds()) / 3600
            event.duration_upper = ((event_end - event_start).total_seconds()) / 3600
            event.people_lower = 1
            event.people_upper = 100
            event.source_type = SEARCH_ENTITY_SOURCES[1]
            event.source_id = raw_data.event_id.event_id
            event.dates = [[event_start, event_end]]
            event.external_link = raw_data.data["url"]
            event.attributes = {
                "eventbrite_event_id": raw_data.event_id.event_id,
            } | self._determine_filters(raw_data)
            new_image = SearchImage(
                link_url=raw_data.data["logo"]["original"]["url"],
                alt_text=raw_data.data["name"]["text"],
                uploaded_by=get_or_create_api_user(),
            )
            self._update_description(event, raw_data.event_id.event_id)
            new_image.save()
            place = self._build_place(event, raw_data)
            event.save()
            event.images.add(new_image)
            event.places.add(place)
        except (KeyError, ValueError, TypeError, IntegrityError, TransportError) as e:
            logging.error(
                f"Unable to create a new event for id {raw_data.event_id.event_id}, error {e}.",
            )
            return False

    def process_data(self):
        """Process the latest EventBrite data into actual events."""
        all_events = EventBriteEventID.objects.filter(
            last_seen__gt=timezone.now() - timedelta(hours=EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS),
        )
        for event_id in all_events:

            try:
                event_raw_data = EventBriteRawEventData.objects.get(event_id=event_id)
            except EventBriteRawEventData.DoesNotExist:
                continue

            try:
                event = Event.objects.get(attributes__eventbrite_event_id=event_id.event_id)
                if not self._has_event_changed(event, event_raw_data):
                    continue
            except Event.DoesNotExist:
                event = Event()
            except Event.MultipleObjectsReturned:
                event = Event.objects.filter(
                    attributes__eventbrite_event_id=event_id.event_id,
                ).first()
                event.delete()
                continue

            self._populate_event(event, event_raw_data)
