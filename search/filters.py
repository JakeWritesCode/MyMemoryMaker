# -*- coding: utf-8 -*-
"""Code relating to dealing with boolean filters stored in the attributes HStoreField."""

# 3rd-party
from typing import Union

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

# Project
from search.constants import FILTERS
from search.models import Activity, Event, Place


def format_field_or_category_name(input: str):
    """Format a field or category name."""
    output = input.replace("_", " ")
    output = output[0].upper() + output[1:]
    return output

class FilterSettingForm(forms.Form):
    """A dynamic form factory for setting filter attributes on a new activity, event or place."""

    def __init__(self, *args, **kwargs):
        """Generate fields based on data from constants.FILTERS."""
        super(FilterSettingForm, self).__init__(*args, **kwargs)
        self.fields = self._generate_fields()

        self.helper = FormHelper()
        self.helper.layout = self._generate_form_layout()



    def _generate_fields(self):
        """
        Generate fields for form dynamically based on data from constants.

        All fields stored within HStore are boolean values.
        So generate a field for each as a checkbox.
        """
        generated_fields = {}

        for field_list in FILTERS.values():
            for field in field_list:
                generated_fields[field] = forms.BooleanField(
                    label=format_field_or_category_name(field),
                    widget=forms.CheckboxInput(
                        attrs={
                            "class": "form-check-input",
                            "role": "switch",
                            "form-field-type": "filter",
                            "onchange": "updatePreviewCard('filters', 'changed')",
                            "human-readable": format_field_or_category_name(field),
                        },
                    ),
                    required=False,
                )

        return generated_fields

    def _generate_form_layout(self):
        """Generate a crispy forms layout for all fields."""
        all_categories = []
        for category_name, filter_list in FILTERS.items():
            category_layout = [
                HTML(f"<h3>{format_field_or_category_name(category_name)}</h3>"),
            ]
            category_layout += [
                Column(
                    Field(field, wrapper_class="form-check form-switch"),
                    css_class="col-md-4 mb-0",
                )
                for field in filter_list
            ]
            all_categories.append(Row(*category_layout, css_class="row mb-2"))

        return Layout(*all_categories)

    def _parse_to_json(self):
        """Parse the data."""
        if not self.is_bound:
            raise ValueError("You need to bind the form to parse to JSON.")
        return_dict = {}
        for category, filter_list in FILTERS.items():
            category_dict = {}
            for filter_str in filter_list:
                if filter_str in self.data.keys():
                    category_dict[filter_str] = True
                else:
                    category_dict[filter_str] = False
            return_dict[category] = category_dict
        return return_dict

    def save(self):
        """Override the save functionality to return the parsed form data as JSON."""
        return self._parse_to_json()


class FilterSearchForm(forms.Form):
    """
    Form to allow for searching by filters.

    Note that this form isn't really processed, but is used to create a big dict in JS
    that is then fed as GET params to a search view on the fly.
    """

    activity_select = forms.BooleanField()
    event_select = forms.BooleanField()
    place_select = forms.BooleanField()

    location = forms.CharField()
    location_lat = forms.CharField(widget=forms.HiddenInput())
    location_long = forms.CharField(widget=forms.HiddenInput())

    distance_lower = forms.IntegerField()
    distance_upper = forms.IntegerField()

    price_lower = forms.IntegerField()
    price_upper = forms.IntegerField()

    duration_lower = forms.IntegerField()
    duration_upper = forms.IntegerField()

    people_lower = forms.IntegerField()
    people_upper = forms.IntegerField()

    datetime_from = forms.DateTimeField()
    datetime_to = forms.DateTimeField()

    keywords = forms.CharField()

    # Filters are automatically generated on class init.

    def __init__(self):
        """Auto-generate filters on init."""
        super(FilterSearchForm, self).__init__()

        # Field formatting
        self.fields["activity_select"].widget.attrs["class"] = "d-none"
        self.fields["event_select"].widget.attrs["class"] = "d-none"
        self.fields["place_select"].widget.attrs["class"] = "d-none"
        self.fields["datetime_from"].widget.attrs["class"] = "form-control"
        self.fields["datetime_to"].widget.attrs["class"] = "form-control"
        self.fields["distance_lower"].widget = forms.HiddenInput()
        self.fields["distance_upper"].widget = forms.HiddenInput()
        self.fields["price_lower"].widget = forms.HiddenInput()
        self.fields["price_upper"].widget = forms.HiddenInput()
        self.fields["people_lower"].widget = forms.HiddenInput()
        self.fields["people_upper"].widget = forms.HiddenInput()

        for field in self.fields.values():
            try:
                field.widget.attrs["class"] += " search-on-change"
            except KeyError:
                field.widget.attrs["class"] = "search-on-change"
            field.required = False


class FilterQueryProcessor:
    """
    Processes an incoming dict created from FilterSearchForm into an ORM query.

    Can run the query, then return a list of Activities, event and places.
    """

    def __init__(self, request_get):  # noqa: D102
        self.request_get = request_get

    def parse_get_into_query(self, query_obj: Union[Activity, Event, Place]):
        """
        Parse a given GET request into a query for the Django ORM.

        The query differs slightly between activity, event and place.
        """
        orm_query = {}

        gt_filters = ["price_lower", "duration_lower", "people_lower"]
        for filter in gt_filters:
            pass