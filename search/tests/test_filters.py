# -*- coding: utf-8 -*-
"""Tests for HStore filters."""

# Standard Library
import datetime
import random
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

# 3rd-party
from crispy_forms.helper import FormHelper
from django import forms
from django.test import SimpleTestCase
from django.test import TestCase

# Project
from search.constants import FILTERS
from search.filters import FilterQueryProcessor
from search.filters import FilterSearchForm
from search.filters import FilterSettingForm
from search.filters import format_field_or_category_name
from search.models import Activity
from search.models import Event
from search.models import Place
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory


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
        assert format_field_or_category_name("test_field") == "Test field"
        assert format_field_or_category_name("I_am_Groot") == "I am Groot"

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
                assert fields[filter_str].label == format_field_or_category_name(
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
                == f"<h3>{format_field_or_category_name(category)}</h3>"
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
        """The returned JSON should just ber a flat list of k/v pairs."""
        expected_dict = {}
        for _category, filter_list in FILTERS.items():
            filters_post = {x: True for x in filter_list}
            expected_dict |= filters_post

        self.form = FilterSettingForm(self.fake_post_data)
        assert self.form._parse_to_json() == expected_dict

    def test_parse_to_json_fills_in_false_selections(self):
        """Unchecked boxes do not get returned at all in HTML. Assume missing is false."""
        random_keys = []
        for _ in range(3):
            random_key = random.choice(list(self.fake_post_data.keys()))
            random_keys.append(random_key)
            self.fake_post_data.pop(random_key)

        flat_filters = FilterSettingForm(self.fake_post_data)._parse_to_json()

        for key in random_keys:
            assert not flat_filters[key]

    def test_save_returns_results_of_parse_to_json(self):
        """Save function should just return parsed results."""
        self.form = FilterSettingForm(self.fake_post_data)
        assert self.form.save() == self.form._parse_to_json()


class TestFilterSelectForm(SimpleTestCase):
    """Tests for the FilterSelectForm."""

    def setUp(self) -> None:  # noqa: D102
        self.form = FilterSearchForm()

    def test_field_definitions(self):
        """Test all field definitions."""
        assert isinstance(self.form.fields["activity_select"], forms.BooleanField)
        assert isinstance(self.form.fields["event_select"], forms.BooleanField)
        assert isinstance(self.form.fields["place_select"], forms.BooleanField)
        assert isinstance(self.form.fields["location"], forms.CharField)
        assert isinstance(self.form.fields["location_lat"], forms.CharField)
        assert isinstance(self.form.fields["location_long"], forms.CharField)
        assert isinstance(self.form.fields["location_lat"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["location_long"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["distance_lower"], forms.IntegerField)
        assert isinstance(self.form.fields["distance_upper"], forms.IntegerField)
        assert isinstance(self.form.fields["price_lower"], forms.IntegerField)
        assert isinstance(self.form.fields["price_upper"], forms.IntegerField)
        assert isinstance(self.form.fields["duration_lower"], forms.IntegerField)
        assert isinstance(self.form.fields["duration_upper"], forms.IntegerField)
        assert isinstance(self.form.fields["people_lower"], forms.IntegerField)
        assert isinstance(self.form.fields["people_upper"], forms.IntegerField)
        assert isinstance(self.form.fields["datetime_from"], forms.DateTimeField)
        assert isinstance(self.form.fields["datetime_to"], forms.DateTimeField)
        assert isinstance(self.form.fields["keywords"], forms.CharField)

    def test_init_params(self):
        """Test form visual modifications as part of init."""
        assert "d-none" in self.form.fields["activity_select"].widget.attrs["class"]
        assert "d-none" in self.form.fields["event_select"].widget.attrs["class"]
        assert "d-none" in self.form.fields["place_select"].widget.attrs["class"]
        assert "form-control" in self.form.fields["datetime_from"].widget.attrs["class"]
        assert "form-control" in self.form.fields["datetime_to"].widget.attrs["class"]
        assert isinstance(self.form.fields["distance_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["distance_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["price_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["price_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["people_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["people_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["duration_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["duration_lower"].widget, forms.HiddenInput)

        for field in self.form.fields.values():
            assert "search-on-change" in field.widget.attrs["class"]
            assert field.required is False


class TestFilterQueryProcessor(TestCase):
    """
    Tests for the FilterQueryProcessor.

    A class designed to parse and execute filter search requests.
    """

    def setUp(self) -> None:  # noqa: D102
        self.processor = FilterQueryProcessor

    def test_init(self):
        """Test class init."""
        processor = self.processor("Tomatoes")
        assert processor.request_get == "Tomatoes"

    def test_types_required_returns_correct_types_required(self):
        """Function should return the base classes of the search entity types selected."""
        get_data = {"activity_select": True}
        assert self.processor(get_data)._types_required() == [Activity]

        get_data = {"activity_select": True, "event_select": True}
        assert self.processor(get_data)._types_required() == [Activity, Event]

        get_data = {"activity_select": True, "event_select": True, "place_select": True}
        assert self.processor(get_data)._types_required() == [Activity, Event, Place]

    def test_types_required_returns_all_if_none_selected(self):
        """If the user does not select a single search entity type, its implied they want all."""
        get_data = {}
        assert self.processor(get_data)._types_required() == [Activity, Event, Place]

    def test_parse_datepicker_datetime(self):
        """Function should parse a datepicker request into a datetime object."""
        assert (
            self.processor({}).parse_datepicker_datetime(
                "12/05/1994, 04:30",
            )
            == datetime.datetime(1994, 5, 12, 4, 30)
        )

    def test_append_slider_queries_gets_the_intersection_right(self):
        """The function should return entities that have an intersection with user upper / lower."""
        activity = ActivityFactory(price_lower=20, price_upper=100)
        qs = Activity.objects.filter()

        get_params = {"price_lower": 10, "price_upper": 50}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

        get_params = {"price_lower": 50, "price_upper": 150}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

        get_params = {"price_lower": 5, "price_upper": 15}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

        get_params = {"price_lower": 150, "price_upper": 170}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

    def test_append_slider_queries_uses_defaults_if_upper_or_lower_not_provided(self):
        """If either slider is not provided, use the default upper or lower bounds."""
        activity = ActivityFactory(price_lower=20, price_upper=100)
        qs = Activity.objects.filter()

        get_params = {"price_lower": 50}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

        get_params = {"price_upper": 50}
        results = list(self.processor(get_params)._append_slider_queries(qs).all())
        assert results == [activity]

    def test_append_search_queries_returns_headline_match(self):
        """Search queries should return a direct word match in headline."""
        activity = ActivityFactory(headline="I love pasta")
        qs = Activity.objects.filter()
        get_param = {"keywords": "pasta"}
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == [activity]
        activity.headline = "I love noodles"
        activity.save()
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == []

    def test_append_search_queries_returns_synonyms_match(self):
        """Search queries should return a direct word match in synonyms."""
        activity = ActivityFactory(synonyms_keywords=["I", "Love", "Pasta"])
        qs = Activity.objects.filter()
        get_param = {"keywords": "pasta"}
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == [activity]
        activity.synonyms_keywords = ["I", "Love", "noodles"]
        activity.save()
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == []

    def test_append_search_queries_returns_description_match(self):
        """Search queries should return a direct word match in description."""
        activity = ActivityFactory(description="I am starlord")
        qs = Activity.objects.filter()
        get_param = {"keywords": "starlord"}
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == [activity]
        activity.description = "I am barry"
        activity.save()
        assert list(self.processor(get_param)._append_search_queries(qs).all()) == []

    def test_append_null_boolean_filter_queries_finds_and_applies_boolean_queries(self):
        """Function should find and apply boolean queries for everything in FILTERS."""
        for _, filter_list in FILTERS.items():
            for bool_filter in filter_list:
                activity = ActivityFactory(attributes={bool_filter: "True"})
                get_data = {f"filter_{bool_filter}": "false"}
                qs = Activity.objects.filter()
                assert list(self.processor(get_data)._append_null_boolean_filter_queries(qs)) == []
                get_data = {f"filter_{bool_filter}": "true"}
                qs = Activity.objects.filter()
                assert list(self.processor(get_data)._append_null_boolean_filter_queries(qs)) == [
                    activity,
                ]

    def test_get_results_for_object_type_calls_correct_functions_for_activity(self):
        """Function should call all correct functions."""
        processor = self.processor({})
        processor._append_slider_queries = MagicMock(return_value=1)
        processor._append_search_queries = MagicMock(return_value=2)
        processor._append_null_boolean_filter_queries = MagicMock(
            return_value=Activity.objects.filter(),
        )
        result = processor._get_results_for_object_type(Activity)
        processor._append_slider_queries.assert_called_once()
        assert processor._append_slider_queries.call_args_list[0][0][0].model == Activity
        processor._append_search_queries.assert_called_once_with(1)
        processor._append_null_boolean_filter_queries.assert_called_once_with(2)
        assert result == []

    def test_get_results_calls__get_results_for_object_type_for_each_object_in_types_required(self):
        """Function should get results for each specified type."""
        processor = self.processor({})
        processor._get_results_for_object_type = MagicMock()
        processor.get_results()
        processor._get_results_for_object_type.assert_has_calls(
            [call(Activity), call(Event), call(Place)],
            any_order=True,
        )

    def test_get_results_returns_randomised_results_list(self):
        """Function should return randomised results list."""
        activity = ActivityFactory()
        event = EventFactory()
        place = PlaceFactory()
        results = FilterQueryProcessor({}).get_results()
        assert activity in results
        assert event in results
        assert place in results
