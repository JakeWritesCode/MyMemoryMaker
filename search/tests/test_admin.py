# -*- coding: utf-8 -*-
"""Tests for the admin."""
# 3rd-party
from django.test import TestCase
from django.urls import reverse
from django.utils.html import format_html

# Project
from search.admin import ActivityAdmin
from search.admin import EventAdmin
from search.admin import PlaceAdmin
from search.admin import SearchEntityAdmin
from search.models import Activity
from search.models import Event
from search.models import Place
from search.tests.factories import ActivityFactory


class TestSearchEntityAdmin(TestCase):
    """Tests for the SearchEntityAdmin abstract class."""

    def setUp(self) -> None:  # noqa: D102
        self.concrete_subclass = ActivityAdmin(Activity, None)

    def test_list_display(self):
        """Test list display."""
        assert self.concrete_subclass.list_display == [
            "headline",
            "source_type",
            "created_by",
            "approved_by",
            "edit_in_wizard",
        ]

    def test_edit_in_wizard(self):
        """Test edit in wizard link."""
        activity = ActivityFactory()
        expected_reverse = reverse("edit-activity", args=[activity.id])
        assert self.concrete_subclass.edit_in_wizard(activity) == format_html(
            f'<a class="button" href="{expected_reverse}">Edit in Wizard</a>',
        )


class TestActivityAdmin(TestCase):
    """Tests for the ActivityAdmin concrete class."""

    def test_config(self):
        """Test config."""
        assert ActivityAdmin.reverse_func == "edit-activity"
        assert isinstance(ActivityAdmin(Activity, None), SearchEntityAdmin)


class TestPlaceAdmin(TestCase):
    """Tests for the PlaceAdmin concrete class."""

    def test_config(self):
        """Test config."""
        assert PlaceAdmin.reverse_func == "edit-place"
        assert isinstance(PlaceAdmin(Place, None), SearchEntityAdmin)


class TestEventAdmin(TestCase):
    """Tests for the EventAdmin concrete class."""

    def test_config(self):
        """Test config."""
        assert EventAdmin.reverse_func == "edit-event"
        assert isinstance(EventAdmin(Event, None), SearchEntityAdmin)
