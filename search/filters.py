# -*- coding: utf-8 -*-
"""Code relating to dealing with boolean filters stored in the attributes HStoreField."""

# Standard Library
import random
from datetime import datetime
from typing import Type
from typing import Union

# 3rd-party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.db.models import Q
from django.db.models import QuerySet

# Project
from search.constants import FILTERS
from search.models import Activity
from search.models import Event
from search.models import Place


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
        for _category, filter_list in FILTERS.items():
            for filter_str in filter_list:
                if filter_str in self.data.keys():
                    return_dict[filter_str] = True
                else:
                    return_dict[filter_str] = False
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
        self.fields["duration_upper"].widget = forms.HiddenInput()
        self.fields["duration_lower"].widget = forms.HiddenInput()

        for field in self.fields.values():
            try:
                field.widget.attrs["class"] += " search-on-change"
            except KeyError:
                field.widget.attrs["class"] = "search-on-change"
            field.required = False

    def save(self):
        """Raise an error, because this form isn't meant to be saved."""
        raise ValueError("This form isn't meant to be saved!")


class FilterQueryProcessor:
    """
    This class is designed to receive a raw series of get parameters and return
    a list of applicable Activities, Events or Places.
    """  # noqa: D205 D400

    def __init__(self, request_get):  # noqa: D107
        self.request_get = request_get

    def _types_required(self):
        """Which types of search entity are required."""
        required_objects = []
        activity_selected = self.request_get.get("activity_select", False)
        if activity_selected:
            required_objects.append(Activity)
        event_selected = self.request_get.get("event_select", False)
        if event_selected:
            required_objects.append(Event)
        place_selected = self.request_get.get("place_select", False)
        if place_selected:
            required_objects.append(Place)

        # If we're not explitly searching for anything, search for everything.
        if len(required_objects) == 0:
            required_objects = [Activity, Event, Place]

        return required_objects

    def parse_datepicker_datetime(self, input: str):
        """Parse datetime picker return into datetime object."""
        return datetime.strptime(input, "%d/%m/%Y, %H:%M")

    def _append_gt_queries(self, queryset: QuerySet):
        """Parse and append all __gt based queries in the get params."""
        gt_filters = ["price_lower", "duration_lower", "people_lower"]
        for gt_filter in gt_filters:
            selected_filter = self.request_get.get(gt_filter, None)
            if selected_filter:
                queryset = queryset.filter(**{f"{gt_filter}__gte": int(selected_filter)})
        return queryset

    def _append_lt_queries(self, queryset: QuerySet):
        """Parse and append all __lt based queries in the get params."""
        lt_filters = ["price_upper", "duration_upper", "people_upper"]
        for lt_filter in lt_filters:
            selected_filter = self.request_get.get(lt_filter, None)
            if selected_filter:
                queryset = queryset.filter(**{f"{lt_filter}__lte": int(selected_filter)})
        return queryset

    def _append_search_queries(self, queryset: QuerySet):
        # TODO - This feels a bit limited, are there any search packages we can use?
        keywords_filters = self.request_get.get("keywords")
        if keywords_filters:
            queryset = queryset.filter(
                Q(synonyms_keywords__overlap=[x.lower() for x in keywords_filters.split()])
                | Q(headline__search=keywords_filters)
                | Q(description__search=keywords_filters),
            )
        return queryset

    def _append_null_boolean_filter_queries(self, queryset: QuerySet):
        """Append a HStoreField query for each of the returned filter status'."""
        for _category, filter_list in FILTERS.items():
            for nb_filter in filter_list:
                boolean_filter = self.request_get.get(f"filter_{nb_filter}")
                if boolean_filter is not None:
                    boolean_filter = True if boolean_filter == "true" else False
                    queryset = queryset.filter(**{f"attributes__{nb_filter}": str(boolean_filter)})
        return queryset

    def _perform_datetime_query(self, list_of_results: list):
        """Pythonically (for now) filter queryset for event datetimes and place opening times."""
        return list_of_results

    def _perform_distance_query(self, list_of_results: list):
        return list_of_results

    def _get_results_for_object_type(self, query_obj: Type[Union[Activity, Event, Place]]):
        """Run the query and get the results for each type."""
        queryset = query_obj.objects.filter()
        queryset = self._append_gt_queries(queryset)
        queryset = self._append_lt_queries(queryset)
        queryset = self._append_search_queries(queryset)
        queryset = self._append_null_boolean_filter_queries(queryset)

        # These bits are done in Python until I can figure out how to use the SQL better
        # Making them more computationally expensive
        # Do them last so they have a smaller qs to work with
        list_of_results = list(queryset.all())
        if query_obj == Event:
            list_of_results = self._perform_datetime_query(list_of_results)
        if query_obj in [Event, Place]:
            list_of_results = self._perform_distance_query(list_of_results)

        return list_of_results

    def get_results(self):
        """Return all results."""
        all_results = []

        for obj_type in self._types_required():
            all_results += list(self._get_results_for_object_type(obj_type))
        random.shuffle(all_results)

        return all_results
