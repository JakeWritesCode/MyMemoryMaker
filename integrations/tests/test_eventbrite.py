# -*- coding: utf-8 -*-
"""Tests for EventBrite API integration."""

# Standard Library
import pathlib
from http.client import NOT_FOUND
from http.client import OK
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

# 3rd-party
from django.test import TestCase

# Project
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import get_or_create_api_user
from integrations.exceptions import APIError
from integrations.models import EventBriteEventID
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
