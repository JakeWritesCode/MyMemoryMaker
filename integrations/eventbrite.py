# -*- coding: utf-8 -*-
"""EventBrite API integration."""
# Standard Library
import json
import logging
import re
import time
from datetime import datetime
from datetime import timedelta
from http.client import OK

# 3rd-party
import googlemaps
import pytz
import requests
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from pytz import UTC

# Project
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

    def _fetch_page_content(self, page_id: int):
        """Perform a GET request for that page's events."""
        url = f"https://www.eventbrite.co.uk/d/united-kingdom/all-events/?page={page_id}"
        response = http_request_with_backoff("get", url)
        if response.status_code != OK:
            raise APIError(f"The page {url} did not return the correct status.")

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

    def get_event_ids(self):
        """Get and update all event ID's from the EventBrite site."""
        logging.info(f"Beginning EventBrite event ID download @ {timezone.now()}")

        for page_number in range(1, 500):
            page_content = self._fetch_page_content(page_number)

            if not self._check_for_results(page_content):
                logging.info(
                    f"EventBrite event ID downloader ran out of pages on page {page_number}",
                )
                return True

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
        response = requests.get(url)
        if response.status_code != OK:
            raise APIError("The API did not return a correct response.")
        return json.loads(response.content)

    def get_recently_seen_events(self):
        """Get all the recently seen events."""
        all_events = EventBriteEventID.objects.filter(
            last_seen__gt=timezone.now() - timedelta(hours=EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS),
        )
        for event_id in all_events[:10]:
            consecutive_errors = 0
            while True:
                try:
                    event_data = self._get_event_data(event_id.event_id)
                    consecutive_errors = 0
                    break
                except APIError:
                    if consecutive_errors > 5:
                        logging.error(
                            f"The EventBrite API returned {consecutive_errors} errors. Aborting.",
                        )
                        return False
                    time.sleep(1)
            try:
                raw_data = EventBriteRawEventData.objects.get(event_id=event_id)
            except EventBriteRawEventData.DoesNotExist:
                raw_data = EventBriteRawEventData(event_id=event_id)
            raw_data.data = event_data
            raw_data.save()


class EventBriteEventParser:
    """Turn Raw EventBrite data into events."""

    def __init__(self):
        """Create a gmaps client."""
        self.gmaps_client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def _has_event_changed(self, event: Event, raw_data: EventBriteRawEventData):
        """Has the event changed compared to the last time we looked."""
        last_updated = datetime.strptime(raw_data.data["changed"], "%Y-%m-%dT%H:%M:%SZ")
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
        if raw_data.data["category_id"]:
            for _, cat_data in EVENTBRITE_CATEGORY_MAPPING.items():
                if cat_data["id"] == raw_data.data["category_id"]:
                    filters |= {our_filter: True for our_filter in cat_data["our_filters"]}

                    if raw_data.data["subcategory_id"]:
                        for _, subcat_data in EVENTBRITE_CATEGORY_MAPPING.items():
                            if subcat_data["id"] == raw_data.data["subcategory_id"]:
                                filters |= {
                                    our_filter: True for our_filter in subcat_data["our_filters"]
                                }

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
        image.uploaded_image.save(gmaps_data["photo_reference"], temp_image)
        image.save()

    def _build_place(self, event: Event, raw_data: EventBriteRawEventData):
        """
        Build the associated place using the Google maps API.

        This is not guaranteed to work 100% of the time, but we'll follow this process:
        1. Get the venue name and try and find it using the Places API.
        2. We're provided with the lat and long, so check that we've got the right place.
        3. If not, use the address to do an address lookup.
        4. Check against the lat and long.
        5. If nothing works, just manually set the lat, long and address in the place
        and leave it up to manual moderation.
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
        if len(gmaps_places["results"]) > 0:
            gmaps_place = gmaps_places["results"][0]
            # Do we already have a place? If so, use it but update it anyway.
            existing_places = Place.objects.filter(google_maps_place_id=gmaps_place["place_id"])
            if len(existing_places) > 0:
                mmm_place = existing_places[0]
                image = mmm_place.images.first()
            else:
                mmm_place = Place()
                image = SearchImage()

            # Update place data
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
            mmm_place.location_lat = gmaps_place["geometry"]["location"]["lng"]
            mmm_place.attributes = {
                "google_maps_data": {
                    "rating": gmaps_place["rating"],
                    "address": gmaps_place["formatted_address"],
                }
            } | event.attributes
            mmm_place.created_by = get_or_create_api_user()
            mmm_place.save()
            if len(gmaps_place["photos"]) > 0:
                self._build_photo_from_gmaps_data(image, gmaps_place["photos"][0], mmm_place)
                mmm_place.images.add(image)
            return mmm_place

    def _populate_event(self, event: Event, raw_data: EventBriteRawEventData):
        """Populate the event with the latest data from the API."""
        try:
            event.last_updated = timezone.now()
            event.approved_by = None
            event.approval_timestamp = None
            event.created_by = get_or_create_api_user()
            event.headline = raw_data.data["name"]["text"]
            event.description = raw_data.data["description"]["html"]
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
            event.duration_lower = ((event_end - event_start).total_seconds()) / 60
            event.duration_upper = ((event_end - event_start).total_seconds()) / 60

            # TODO - What are we going to do with this?
            event.people_lower = 1
            event.people_upper = 100

            event.source_type = SEARCH_ENTITY_SOURCES[1]

            event.source_id = raw_data.event_id.event_id

            event.dates = [[event_start, event_end]]

            event.attributes = {
                "eventbrite_event_id": raw_data.event_id.event_id,
            } | self._determine_filters(raw_data)

            new_image = SearchImage(
                link_url=raw_data.data["logo"]["original"]["url"],
                alt_text=raw_data.data["name"]["text"],
                uploaded_by=get_or_create_api_user(),
            )
            new_image.save()

            event.save()
            event.images.add(new_image)
            event.places.add(self._build_place(event, raw_data))
        except KeyError:
            return

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

            self._populate_event(event, event_raw_data)
