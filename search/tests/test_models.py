# -*- coding: utf-8 -*-
"""Tests for the search models."""

# 3rd-party
from django.core.exceptions import ValidationError
from django.test import TestCase
from geopy.distance import distance

# Project
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory
from search.tests.factories import SearchImageFactory


class TestSearchImages(TestCase):
    """Tests for SearchImages."""

    def setUp(self) -> None:  # noqa: D102
        self.instance = SearchImageFactory()

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

    def test_display_url_returns_image_url_if_uploaded(self):
        """If the image was uploaded, return path."""
        assert self.instance.display_url == self.instance.uploaded_image.url

    def test_display_url_returns_link_url_if_not_uploaded(self):
        """If the image was uploaded, return path."""
        self.instance.uploaded_image = None
        self.instance.link_url = "hey there!"
        assert self.instance.display_url == "hey there!"


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

    def setUp(self) -> None:  # noqa: D102
        self.instance = PlaceFactory()

    def test_str(self):
        """Test string representation."""
        place = PlaceFactory()
        assert str(place) == f"Place: {place.headline}"

    def test_distance_from_raises_valueerror_if_no_lat_or_long(self):
        """If there's no lat or long, return a ValueError."""
        self.instance.location_lat = None
        with self.assertRaises(ValueError) as e:
            self.instance.distance_from(1, 1)
        assert "We don't know where this place is!" in str(e.exception)

    def test_distance_from_returns_correct_distance(self):
        """Function should return the correct distance."""
        new_lat, new_long = 1, 2
        expected_distance = distance(
            (self.instance.location_lat, self.instance.location_long),
            (new_lat, new_long),
        ).miles
        assert self.instance.distance_from(new_lat, new_long) == expected_distance


class TestEvent(TestCase):
    """Tests for Place."""

    def test_str(self):
        """Test string representation."""
        event = EventFactory()
        assert str(event) == f"Event: {event.headline}"

    def test_distance_from_returns_correct_distance(self):
        """Function should return the correct distance."""
        place = PlaceFactory()
        event = EventFactory()
        event.places.add(place)
        new_lat, new_long = 1, 2
        expected_distance = distance(
            (place.location_lat, place.location_long),
            (new_lat, new_long),
        ).miles
        assert event.distance_from(new_lat, new_long) == expected_distance
