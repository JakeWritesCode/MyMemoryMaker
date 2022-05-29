# -*- coding: utf-8 -*-
"""Forms for search."""

# 3rd-party
from django import forms
from django.contrib.auth.models import AnonymousUser

# Project
from search.constants import SEARCH_ENTITY_SOURCES
from search.models import Activity
from search.models import Place
from search.models import SearchEntity
from search.models import SearchImage


class SearchImageForm(forms.ModelForm):
    """A form for uploading a single search image."""

    permissions_confirmation = forms.BooleanField(
        required=True,
        label="Please confirm you have permission to use and share this image.",
    )

    def __init__(self, user, *args, image_required=True, **kwargs):  # noqa: D107
        self.user = user
        super(SearchImageForm, self).__init__(*args, **kwargs)
        self.fields["uploaded_image"].widget.attrs["class"] = "form-control"
        self.fields["alt_text"].widget.attrs["placeholder"] = "Please describe your image."
        self.fields["link_url"].widget = forms.HiddenInput()
        self.fields["link_url"].required = False

        if not image_required:
            self.fields["uploaded_image"].required = False
            self.fields["alt_text"].required = False
            self.fields["permissions_confirmation"].required = False

    class Meta:  # noqa: D106
        model = SearchImage
        fields = ["link_url", "uploaded_image", "alt_text"]

    def save(self, commit=True):
        """Add the uploading user id."""
        self.instance.uploaded_by = self.user
        return super(SearchImageForm, self).save(commit=commit)


class NewSearchEntityForm(forms.ModelForm):
    """Form for a new search entity."""

    def __init__(self, user, *args, **kwargs):  # noqa: D107
        self.user = user

        if isinstance(user, AnonymousUser) or not user:
            raise ValueError("User must be logged in and passed to this form.")
        super(NewSearchEntityForm, self).__init__(*args, **kwargs)

        # Mess about with widget attributes
        self.fields["headline"].widget.attrs[
            "placeholder"
        ] = "Give us a one sentence summary of your activity."
        self.fields["price_upper"].widget.attrs["class"] = "form-control"
        self.fields["price_lower"].widget.attrs["class"] = "form-control"
        self.fields["duration_upper"].widget.attrs["class"] = "form-control"
        self.fields["duration_lower"].widget.attrs["class"] = "form-control"
        self.fields["people_lower"].widget.attrs["class"] = "form-control"
        self.fields["people_upper"].widget.attrs["class"] = "form-control"
        self.fields["description"].required = False
        self.fields["synonyms_keywords"].widget.attrs[
            "placeholder"
        ] = "Please seperate words or phrases with commas."

    class Meta:  # noqa: D106
        model = SearchEntity
        fields = [
            "headline",
            "description",
            "price_upper",
            "price_lower",
            "duration_upper",
            "duration_lower",
            "people_lower",
            "people_upper",
            "synonyms_keywords",
        ]

    def save(self, commit=True):
        """Enrich the instance with attribute data, user data and images."""
        self.instance.created_by = self.user
        try:
            image = self.image
            filters_json = self.filters_json
        except AttributeError:
            raise AttributeError("You need to add the filter data and the image.")
        self.instance.attributes = filters_json
        self.instance.source_type = SEARCH_ENTITY_SOURCES[0]
        super(NewSearchEntityForm, self).save(commit=commit)
        self.instance.images.add(image)
        return self.instance


class NewActivityForm(NewSearchEntityForm):
    """New activity form (same as a search entity form)."""

    class Meta:  # noqa: D106
        model = Activity
        fields = [
            "headline",
            "description",
            "price_upper",
            "price_lower",
            "duration_upper",
            "duration_lower",
            "people_lower",
            "people_upper",
            "synonyms_keywords",
        ]


class NewPlaceForm(NewSearchEntityForm):
    """New place form."""

    place_search = forms.CharField(
        required=True,
        label="Find your place on Google Maps, and we'll use it to get some inital information.",
    )
    google_maps_rating = forms.FloatField(required=False)
    address = forms.CharField(widget=forms.TextInput)

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(NewPlaceForm, self).__init__(*args, **kwargs)
        self.fields["google_maps_place_id"].widget = forms.HiddenInput()
        self.fields["location_lat"].widget = forms.HiddenInput()
        self.fields["location_long"].widget = forms.HiddenInput()
        self.fields["google_maps_rating"].widget = forms.HiddenInput()
        self.fields["google_maps_rating"].required = False
        self.fields["address"].widget = forms.HiddenInput()
        self.fields["activities"].required = False

    class Meta:  # noqa: D106
        model = Place
        fields = [
            "headline",
            "description",
            "price_upper",
            "price_lower",
            "duration_upper",
            "duration_lower",
            "people_lower",
            "people_upper",
            "synonyms_keywords",
            "google_maps_place_id",
            "activities",
            "location_lat",
            "location_long",
        ]
