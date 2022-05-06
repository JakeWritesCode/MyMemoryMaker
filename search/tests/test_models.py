# -*- coding: utf-8 -*-
"""Tests for the search models."""

# 3rd-party
from django.test import TestCase

# Project
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory
from search.tests.factories import SearchImageFactory


class TestSearchImages(TestCase):
    """Tests for SearchImages."""

    def test_str(self):
        """Test string representation."""
        image = SearchImageFactory()
        assert str(image) == f"Search Uploaded Image {image.id}: {image.alt_text}"


class TestActivity(TestCase):
    """Tests for Activity."""

    def test_str(self):
        """Test string representation."""
        activity = ActivityFactory()
        assert str(activity) == f"Activity: {activity.headline}"


class TestPlace(TestCase):
    """Tests for Place."""

    def test_str(self):
        """Test string representation."""
        place = PlaceFactory()
        assert str(place) == f"Place: {place.headline}"


class TestEvent(TestCase):
    """Tests for Place."""

    def test_str(self):
        """Test string representation."""
        event = EventFactory()
        assert str(event) == f"Event: {event.headline}"
