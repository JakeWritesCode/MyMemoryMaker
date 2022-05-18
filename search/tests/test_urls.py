# -*- coding: utf-8 -*-
"""Tests for urls.py."""


# 3rd-party
from django.test import SimpleTestCase
from django.urls import reverse

# Project
from search import views


class TestURLs(SimpleTestCase):
    """Test URLS for users app."""

    def test_sign_up_url(self):
        """Test url."""
        assert reverse(views.new_activity) == "/search/new-activity"

    def test_search_results_url(self):
        """Test url."""
        assert reverse(views.search_results) == "/search/search-results"

    def test_search_view_url(self):
        """Test url."""
        assert reverse(views.search_view) == "/search/"