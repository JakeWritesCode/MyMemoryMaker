# -*- coding: utf-8 -*-
"""Tests for EventBrite API integration."""

# Standard Library
import json
import pathlib
from datetime import timedelta

from django.utils import timezone
from http.client import NOT_FOUND
from http.client import OK
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

# 3rd-party
from django.conf import settings
from django.test import TestCase

# Project
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader
from integrations.eventbrite import get_or_create_api_user
from integrations.exceptions import APIError
from integrations.models import EventBriteEventID
from integrations.tests.factories import EventBriteEventIDFactory
from users.models import CustomUser


class TestGetOrCreateAPIUser(TestCase):
    """Tests for the get_or_create_api_user function."""

    def test_function_creates_new_user_if_does_not_exist(self):
        """If there is no existing integrations user, create one and return."""
        assert CustomUser.objects.count() == 0
        user = get_or_create_api_user()
        assert CustomUser.objects.count() == 1
        assert user.email == "integrations@mymemorymaker.com"
        assert user.first_name == "MyMemoryMaker"
        assert user.last_name == "Integrations API"

    def test_function_returns_integrations_user_if_one_exists(self):
        """If there is an existing integrations user, return."""
        get_or_create_api_user()
        assert CustomUser.objects.count() == 1
        user = get_or_create_api_user()
        assert CustomUser.objects.count() == 1
        assert user.email == "integrations@mymemorymaker.com"
        assert user.first_name == "MyMemoryMaker"
        assert user.last_name == "Integrations API"


class TestEventIDDownloader(TestCase):
    """Tests for the EventIDDownloader class."""

    def setUp(self) -> None:  # noqa: D102
        self.downloader = EventIDDownloader()
        self.expected_ids = [
            "211654312747",
            "298291005427",
            "253332112167",
            "92050063217",
            "229624421827",
            "328337816247",
            "287917247237",
            "294605391657",
            "219186220887",
            "274947704987",
            "331450917617",
            "209398495537",
            "317664341597",
            "170284340045",
            "267762253107",
            "272765217107",
            "327437102187",
            "330544877627",
            "163761255323",
            "207339938337",
        ]

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__fetch_page_content_calls_request_backoff_with_correct_url(self, mock_backoff):
        """The function should call the correct url."""
        mock_backoff.return_value = MagicMock(status_code=OK, content=b"Hey!")
        self.downloader._fetch_page_content(1)
        mock_backoff.assert_called_once_with(
            "get",
            "https://www.eventbrite.co.uk/d/united-kingdom/all-events/?page=1",
        )

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__fetch_page_content_raises_apierror_if_status_code_incorrect(self, mock_backoff):
        """The function should raise an APIError if the status code is incorrect."""
        url = "https://www.eventbrite.co.uk/d/united-kingdom/all-events/?page=1"
        mock_backoff.return_value = MagicMock(status_code=NOT_FOUND, content=b"Hey!")
        with self.assertRaises(APIError) as e:
            self.downloader._fetch_page_content(1)
        assert f"The page {url} did not return the correct status." in str(e.exception)

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__fetch_page_content_returns_stringified_page_content(self, mock_backoff):
        """The function should return the response data as a string."""
        mock_backoff.return_value = MagicMock(status_code=OK, content=b"Hey!")
        response = self.downloader._fetch_page_content(1)
        assert response == "b'Hey!'"

    def test__check_for_results_returns_false_if_string_match_found_in_page_content(self):
        """The function should return false if the no more results text is found in the page."""
        assert (
            self.downloader._check_for_results(
                "Nothing matched your search, but you might like these options.",
            )
            is False
        )

    def test__check_for_results_returns_true_if_string_match_not_found_in_page_content(self):
        """The function should return true if the not more results text is not found in the page."""
        assert self.downloader._check_for_results("Loads of results!") is True

    def test_functional_eventbrite_actually_shows_the_right_text(self):
        """
        This whole thing working actually relies on EventBrite not changing that text.

        Actually call the page and make sure they haven't changed it.
        """
        response = self.downloader._fetch_page_content(5000)
        assert "Nothing matched your search, but you might like these options." in response

    def test__get_event_ids_from_page_gets_the_correct_ids(self):
        """The function should get the correct event ID's from the page content."""
        file = pathlib.Path(__file__).parent.resolve()
        with open(f"{file}/mock_api_data/eventbrite_results_page.txt", "r") as sample_page:
            event_ids = self.downloader._get_event_ids_from_page(sample_page.read())

            for exp_id in self.expected_ids:
                assert exp_id in event_ids

    def test_get_event_ids_loops_through_pages_until_no_more_results(self):
        """Function should loop through results until there are no more."""
        self.downloader._fetch_page_content = MagicMock(return_value="Test Data")
        self.downloader._check_for_results = MagicMock(side_effect=[True, True, True, False])
        response = self.downloader.get_event_ids()
        assert response is True
        self.downloader._fetch_page_content.assert_has_calls(
            [
                call(1),
                call(2),
                call(3),
                call(4),
            ],
        )
        assert self.downloader._fetch_page_content.call_count == 4

    def test_get_event_ids_saves_event_ids_to_db(self):
        """Function should save the event ID's to the DB."""
        assert EventBriteEventID.objects.count() == 0
        file = pathlib.Path(__file__).parent.resolve()
        with open(f"{file}/mock_api_data/eventbrite_results_page.txt", "r") as sample_page:
            self.downloader._fetch_page_content = MagicMock(
                side_effect=[
                    sample_page.read(),
                    "Nothing matched your search, but you might like these options.",
                ],
            )
        self.downloader.get_event_ids()
        assert EventBriteEventID.objects.count() == len(self.expected_ids)


class TestEventRawDataDownloader(TestCase):
    """Tests for the EventRawDataDownloader class."""

    def setUp(self) -> None:  # noqa: D102
        self.downloader = EventRawDataDownloader()
        self.event_ids = [
            EventBriteEventIDFactory(),
            EventBriteEventIDFactory(),
            EventBriteEventIDFactory(),
        ]
        settings.EVENTBRITE_API_KEY = "ABC123"

        file = pathlib.Path(__file__).parent.resolve()
        with open(f"{file}/mock_api_data/eventbrite_event_data.json", "r") as sample_return:
             self.sample_json = json.load(sample_return)

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__get_event_data_calls_correct_api_url(self, mock_get):
        """Function should call the correct API URL."""
        mock_get.return_value = MagicMock(status_code=OK, content=b"{}")
        self.downloader._get_event_data("1234")
        mock_get.assert_called_once_with(
            "get",
            f"https://www.eventbriteapi.com/v3/events/1234/"
            f"?expand=category,subcategory,venue,format,listing_properties,ticket_availability"
            f"&token={settings.EVENTBRITE_API_KEY}"
        )

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__get_event_data_raises_apierror_if_incorrect_status(self, mock_get):
        """Function should raise an API error if the response was not correct."""
        mock_get.return_value = MagicMock(status_code=NOT_FOUND, content=b"{}")
        with self.assertRaises(APIError) as e:
            self.downloader._get_event_data("1234")
        assert "The API did not return a correct response." in str(e.exception)

    @patch("integrations.eventbrite.http_request_with_backoff")
    def test__get_event_data_returns_loaded_json(self, mock_get):
        """Function should return the loaded JSON response."""
        mock_get.return_value = MagicMock(status_code=OK, content=b'{"Hey": "There!"}')
        response = self.downloader._get_event_data("1234")
        assert response == {"Hey": "There!"}

    def test_get_recently_seen_events_only_get_events_last_seen_in_timeframe(self):
        """Function should only download events recently seen on ID download."""
        self.downloader._get_event_data = MagicMock(return_value=self.sample_json)
        self.downloader.get_recently_seen_events()
        self.downloader._get_event_data.assert_has_calls(
            [call(x.event_id) for x in self.event_ids], any_order=True,
        )

        for event_id in self.event_ids:
            event_id.last_seen = timezone.now() - timedelta(days=10)
            event_id.save()

        self.downloader._get_event_data.reset_mock()
        self.downloader.get_recently_seen_events()
        self.downloader._get_event_data.assert_not_called()