# -*- coding: utf-8 -*-
"""Tests for the search models."""

# 3rd-party
from django.core.exceptions import ValidationError
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

    def test_cannot_save_an_image_with_no_url_or_s3_key(self):
        """Images need to either have a URL or an S3 key."""
        image = SearchImageFactory()
        image.uploaded_image = None
        image.link_url = None
        with self.assertRaises(ValidationError) as e:
            image.save()
        assert "You must either add an uploaded image or specify an S3 URL." in str(e.exception)


class TestActivity(TestCase):
    """Tests for Activity."""

    def test_str(self):
        """Test string representation."""
        activity = ActivityFactory()
        assert str(activity) == f"Activity: {activity.headline}"

    def test_save_calls_clean_synonyms_keywords(self):
        """Save should call clean method."""
        entity = ActivityFactory(synonyms_keywords=["Whats", "Up", "Doc"])
        entity.save()
        assert entity.synonyms_keywords == ["whats", "up", "doc"]

    def test_clean_synonyms_keywords_lowers_case(self):
        """Clean function should lower case."""
        entity = ActivityFactory(synonyms_keywords=["Whats", "Up", "Doc"])
        entity.clean_synonyms_keywords()
        assert entity.synonyms_keywords == ["whats", "up", "doc"]

    def test_active_filters_returns_active_filters(self):
        """Property should return a flat list of all active filters."""
        entity = ActivityFactory(
            attributes={"filter": "True", "not": "False", "selected": "True"},
        )
        assert entity.active_filters == ["filter", "selected"]


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
