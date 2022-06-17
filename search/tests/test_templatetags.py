# -*- coding: utf-8 -*-
"""Tests for templatetags."""

# 3rd-party
from django.test import TestCase

# Project
from search.templatetags.literal_eval import ast_literal_eval


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
