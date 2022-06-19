# -*- coding: utf-8 -*-
"""Tests for urls.py."""


# 3rd-party
from django.test import SimpleTestCase
from django.urls import reverse

# Project
from search import views


class TestURLs(SimpleTestCase):
    """Test URLS for users app."""

    def test_new_activity_url(self):
        """Test url."""
        assert reverse(views.new_activity) == "/search/new-activity"

    def test_edit_activity_url(self):
        """Test url."""
        assert reverse(views.edit_activity, args=["a123"]) == "/search/edit-activity/a123"

    def test_new_place_url(self):
        """Test url."""
        assert reverse(views.new_place) == "/search/new-place"

    def test_edit_place_url(self):
        """Test url."""
        assert reverse(views.edit_place, args=["a123"]) == "/search/edit-place/a123"

    def test_search_results_url(self):
        """Test url."""
        assert reverse(views.search_results) == "/search/search-results"

    def test_edit_event_url(self):
        """Test url."""
        assert reverse(views.edit_event, args=["a123"]) == "/search/edit-event/a123"

    def test_search_view_url(self):
        """Test url."""
        assert reverse(views.search_view) == "/search/"

    def test_new_submission_url(self):
        """Test url."""
        assert reverse(views.new_entity_wizard) == "/search/new-submission"

    def test_see_more_url(self):
        """Test url."""
        assert reverse(views.see_more, args=["Event", "a123"]) == "/search/see-more/Event/a123"

    def test_add_to_wishlist_url(self):
        """Test url."""
        assert reverse(views.add_to_wishlist, args=["Event", "a123"]) == "/search/add-to-wishlist/Event/a123"
