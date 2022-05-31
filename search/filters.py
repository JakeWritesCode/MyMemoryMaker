# -*- coding: utf-8 -*-
"""Code relating to dealing with boolean filters stored in the attributes HStoreField."""

# Standard Library
import random
from datetime import datetime
from typing import Type
from typing import Union

# 3rd-party
import pytz
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.db.models import Q
from django.db.models import QuerySet
from django.utils import timezone

# Project
from search.constants import FILTERS
from search.constants import GT_LT_FILTERS_UPPER_LOWER_BOUNDS
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

    def _append_slider_queries(self, queryset: QuerySet):
        """
        Append any slider queries to the qs.

        For slider queries, we want to provide any intersection between the upper and lower bounds
        if the search entity and the user selection.
        So...
                |---User Selection ---|
        |---Search entity 1 --|
                                |---Search entity 2---|
                                       |---Search entity 3---|
        We want to provide search entities 1 and 2 and allow the user to make a decision as to the
        suitability on their own.

        Filters should always come in pairs but if they don't, add the upper and lower bounds
        from constants.
        """
        filter_sets = [
            # [lower_name, upper_name, lower default, upper default]
            [
                "price_lower",
                "price_upper",
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["price"][0],
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["price"][1],
            ],
            [
                "duration_lower",
                "duration_upper",
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["duration"][0],
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["duration"][1],
            ],
            [
                "people_lower",
                "people_upper",
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["people"][0],
                GT_LT_FILTERS_UPPER_LOWER_BOUNDS["people"][1],
            ],
        ]

        for filter_set in filter_sets:
            lower_selected = self.request_get.get(filter_set[0], None)
            upper_selected = self.request_get.get(filter_set[1], None)
            if lower_selected or upper_selected:
                if not lower_selected:
                    lower_selected = filter_set[2]
                if not upper_selected:
                    upper_selected = filter_set[3]
                # User selected low needs to be less than entity high
                # AND
                # User selected high needs to be more than entity low
                queryset = queryset.filter(**{f"{filter_set[1]}__gte": lower_selected})
                queryset = queryset.filter(**{f"{filter_set[0]}__lte": upper_selected})

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
        datetime_from = self.request_get.get("datetime_from", None)
        datetime_to = self.request_get.get("datetime_to", None)

        try:
            datetime_from = datetime.strptime(datetime_from, "%d/%m/%Y, %H:%M")
            datetime_from = timezone.make_aware(
                datetime_from,
                timezone=pytz.timezone("Europe/London"),
            )
        except (ValueError, TypeError):
            datetime_from = None

        try:
            datetime_to = datetime.strptime(datetime_to, "%d/%m/%Y, %H:%M")
            datetime_to = timezone.make_aware(datetime_to, timezone=pytz.timezone("Europe/London"))
        except (ValueError, TypeError):
            datetime_to = None

        if not datetime_from and not datetime_to:
            return list_of_results

        date_match = []
        for event in list_of_results:
            added = False
            for date_set in event.dates:
                if added:
                    continue
                if datetime_from:
                    if datetime_from < date_set[1]:
                        date_match.append(event)
                        added = True
                        continue
                if datetime_to:
                    if datetime_to > date_set[0]:
                        date_match.append(event)
                        added = True
                        continue

        return date_match

    def _perform_distance_query(self, list_of_results: list):
        """Do this in Python for now. It's expensive though."""
        lat_selected = self.request_get.get("location_lat", None)
        long_selected = self.request_get.get("location_long", None)
        distance_lower = self.request_get.get("distance_lower", None)
        distance_upper = self.request_get.get("distance_upper", None)

        if not lat_selected or not long_selected or not distance_lower or not distance_upper:
            if distance_lower != 0:
                return list_of_results

        try:
            lat_selected = float(lat_selected)
            long_selected = float(long_selected)
            distance_lower = int(distance_lower)
            distance_upper = int(distance_upper)
        except ValueError:
            return list_of_results

        return [
            x
            for x in list_of_results
            if distance_lower <= x.distance_from(lat_selected, long_selected) <= distance_upper
        ]

    def _get_results_for_object_type(self, query_obj: Type[Union[Activity, Event, Place]]):
        """Run the query and get the results for each type."""
        queryset = query_obj.objects.filter()
        queryset = self._append_slider_queries(queryset)
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
