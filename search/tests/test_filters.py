# -*- coding: utf-8 -*-
"""Tests for HStore filters."""

# Standard Library
import random
from unittest.mock import patch

# 3rd-party
from crispy_forms.helper import FormHelper
from django import forms
from django.test import SimpleTestCase

# Project
from search.constants import FILTERS
from search.filters import FilterSettingForm


class TestFilterSettingForm(SimpleTestCase):
    """Tests for the dynamic FilterSettingForm."""

    def setUp(self) -> None:  # noqa: D102
        self.form = FilterSettingForm()

        self.fake_post_data = {}
        for _, filter_list in FILTERS.items():
            for filter_str in filter_list:
                self.fake_post_data[filter_str] = True

    def test_form_subclasses_django_form(self):
        """Form should inherit django form functionality."""
        assert isinstance(self.form, forms.Form)

    @patch(
        "search.tests.test_filters.FilterSettingForm._generate_form_layout",
        return_value="_generate_form_layout()",
    )
    @patch(
        "search.tests.test_filters.FilterSettingForm._generate_fields",
        return_value="_generate_fields()",
    )
    def test_init(self, mock_fields, mock_layout):
        """Test class initialisation."""
        form = FilterSettingForm()
        assert form.fields == "_generate_fields()"
        assert isinstance(form.helper, FormHelper)
        assert form.helper.layout == "_generate_form_layout()"

    def test_format_field_or_category_name_formats_correctly(self):
        """Function should format the slugified string into human-readable text."""
        assert self.form._format_field_or_category_name("test_field") == "Test field"
        assert self.form._format_field_or_category_name("I_am_Groot") == "I am Groot"

    def test_generate_fields_generates_a_field_for_each_filter_in_constants(self):
        """Function should generate a field for each filter specified in constants.FILTERS."""
        fields = self.form._generate_fields()
        for category_list in FILTERS.values():
            for filter_str in category_list:
                assert filter_str in fields.keys()

    def test_generate_fields_generates_correct_field_for_each_filter(self):
        """All generated fields should be the correct type with the correct params."""
        fields = self.form._generate_fields()
        for category_list in FILTERS.values():
            for filter_str in category_list:
                assert isinstance(fields[filter_str], forms.BooleanField)
                assert fields[filter_str].label == self.form._format_field_or_category_name(
                    filter_str,
                )
                assert isinstance(fields[filter_str].widget, forms.CheckboxInput)
                assert fields[filter_str].widget.attrs["class"] == "form-check-input"
                assert fields[filter_str].widget.attrs["role"] == "switch"
                assert fields[filter_str].required is False

    def test_generate_form_layout_generates_one_row_per_category_in_filters(self):
        """The function should generate one row per filters category."""
        assert len(self.form.helper.layout.fields) == len(FILTERS.keys())

    def test_generate_form_layout_generates_h3_objects_for_each_category_name(self):
        """Each category should have a corresponding H3 tag with the category name."""
        for index, category in enumerate(FILTERS.keys()):
            assert (
                self.form.helper.layout.fields[index].fields[0].html
                == f"<h3>{self.form._format_field_or_category_name(category)}</h3>"
            )

    def test_generate_form_layout_generates_a_switch_field_for_each_expected_filter(self):
        """Function should generate a switch layout for each field in the filter."""
        for index, category in enumerate(FILTERS.keys()):
            all_row_fields = []
            for layout_object in self.form.helper.layout.fields[index].fields:
                form_fields = getattr(layout_object, "fields", None)
                if form_fields:
                    for field in form_fields:
                        all_row_fields.append(field)

            for field in FILTERS[category]:
                assert field in [x.fields[0] for x in all_row_fields]

    def test_parse_to_json_raises_valueerror_if_not_bound(self):
        """If the form is not bound, raise a ValueError."""
        with self.assertRaises(ValueError) as e:
            self.form._parse_to_json()
        assert "You need to bind the form to parse to JSON." in str(e.exception)

    def test_parse_to_json_parses_into_correct_format(self):
        """The returned JSON should be in the same format as constants.FILTERS."""
        expected_dict = {}
        for category, filter_list in FILTERS.items():
            filters_post = {x: True for x in filter_list}
            expected_dict[category] = filters_post

        self.form = FilterSettingForm(self.fake_post_data)
        assert self.form._parse_to_json() == expected_dict

    def test_parse_to_json_fills_in_false_selections(self):
        """Unchecked boxes do not get returned at all in HTML. Assume missing is false."""
        random_keys = []
        for _ in range(3):
            random_key = random.choice(list(self.fake_post_data.keys()))
            random_keys.append(random_key)
            self.fake_post_data.pop(random_key)

        flat_filters = {}
        for filters in FilterSettingForm(self.fake_post_data)._parse_to_json().values():
            flat_filters = flat_filters | filters

        for key in random_keys:
            assert not flat_filters[key]

    def test_save_returns_results_of_parse_to_json(self):
        """Save function should just return parsed results."""
        self.form = FilterSettingForm(self.fake_post_data)
        assert self.form.save() == self.form._parse_to_json()
