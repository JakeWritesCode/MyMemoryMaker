# -*- coding: utf-8 -*-
"""Tests for templatetags."""

# Standard Library
from unittest.mock import MagicMock

# 3rd-party
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

# Project
from search.templatetags.is_in_users_wishlist import is_in_users_wishlist
from search.templatetags.literal_eval import ast_literal_eval
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory
from users.tests.factories import CustomUserFactory


class TestLiteralEval(TestCase):
    """Turns a stringified dict back into a dict so it can be queried, also returns a key."""

    def setUp(self) -> None:  # noqa: D102
        self.test_dict = str({"item": "test", "sub_item": {"Stuff": True}})

    def test_function_returns_string_if_no_key_specified(self):
        """If no key was specified, return the literally eval'd object."""
        assert ast_literal_eval(self.test_dict) == {"item": "test", "sub_item": {"Stuff": True}}

    def test_function_returns_value_if_key_specified(self):
        """If a key is specified, return the value for that key."""
        assert ast_literal_eval(self.test_dict, "item") == "test"
        assert ast_literal_eval(self.test_dict, "sub_item") == {"Stuff": True}


class TestIsInUsersWishlist(TestCase):
    """Tests for the is_in_users_wishlist tag."""

    def setUp(self) -> None:  # noqa: D102
        self.activity = ActivityFactory()
        self.activity_not_favourite = ActivityFactory()
        self.event = EventFactory()
        self.event_not_favourite = EventFactory()
        self.place = PlaceFactory()
        self.place_not_favourite = PlaceFactory()
        self.user = CustomUserFactory()
        self.user.wishlist_activities.add(self.activity)
        self.user.wishlist_events.add(self.event)
        self.user.wishlist_places.add(self.place)

    def test_tag_returns_false_if_user_is_not_logged_in(self):
        """Tag should return False if the user is not logged in."""
        context = MagicMock()
        context.request = MagicMock()
        context.request.user = AnonymousUser()

        assert is_in_users_wishlist(context, "Event", "a123") is False

    def test_tag_returns_correct_wishlist_status_activity(self):
        """Tag should return the correct wishlist status for Activity."""
        context = MagicMock()
        context.request = MagicMock()
        context.request.user = self.user

        assert is_in_users_wishlist(context, "Activity", self.activity.id) is True
        assert is_in_users_wishlist(context, "Activity", self.activity_not_favourite.id) is False

    def test_tag_returns_correct_wishlist_status_event(self):
        """Tag should return the correct wishlist status for Event."""
        context = MagicMock()
        context.request = MagicMock()
        context.request.user = self.user

        assert is_in_users_wishlist(context, "Event", self.event.id) is True
        assert is_in_users_wishlist(context, "Event", self.event_not_favourite.id) is False

    def test_tag_returns_correct_wishlist_status_place(self):
        """Tag should return the correct wishlist status for Place."""
        context = MagicMock()
        context.request = MagicMock()
        context.request.user = self.user

        assert is_in_users_wishlist(context, "Place", self.place.id) is True
        assert is_in_users_wishlist(context, "Place", self.place_not_favourite.id) is False
