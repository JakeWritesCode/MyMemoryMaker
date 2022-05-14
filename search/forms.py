# -*- coding: utf-8 -*-
"""Forms for search."""

# 3rd-party
from django import forms
from django.contrib.auth.models import AnonymousUser

# Project
from search.models import Activity
from search.models import SearchImage


def get_activity_choices():
    """Get a list of tuples representing all active activities."""
    choices = [
        (f"{activity.headline} ({', '.join(activity.synonyms)})", activity.id)
        for activity in Activity.objects.filter(approval_timestamp__isnull=False)
    ]
    choices.append(("Create your own...", "create_your_own"))
    return choices


class SearchImageForm(forms.ModelForm):
    """A form for uploading a single search image."""

    permissions_confirmation = forms.BooleanField(
        required=True,
        label="Please confirm you have permission to use and share this image.",
    )

    def __init__(self, user, *args, **kwargs):  # noqa: D107
        self.user = user
        super(SearchImageForm, self).__init__(*args, **kwargs)
        self.fields["uploaded_image"].widget.attrs["class"] = "form-control"
        self.fields["alt_text"].widget.attrs["placeholder"] = "Please describe your image."

    class Meta:  # noqa: D106
        model = SearchImage
        fields = ["uploaded_image", "alt_text"]

    def save(self, commit=True):
        """Add the uploading user id."""
        self.instance.uploaded_by = self.user
        return super(SearchImageForm, self).save(commit=commit)


class ActivitySelectorForm(forms.Form):
    """Tag like form allows you to select multiple activities or start creating a new one."""


class NewActivityForm(forms.ModelForm):
    """Form for a new activity."""

    def __init__(self, user, *args, **kwargs):  # noqa: D107
        self.user = user

        if isinstance(user, AnonymousUser) or not user:
            raise ValueError("User must be logged in and passed to this form.")
        super(NewActivityForm, self).__init__(*args, **kwargs)

        # Mess about with widget attributes
        self.fields["headline"].widget.attrs[
            "placeholder"
        ] = "Give us a one sentence summary of your activity."
        self.fields["price_upper"].widget = forms.HiddenInput()
        self.fields["price_lower"].widget = forms.HiddenInput()
        self.fields["duration_upper"].widget = forms.HiddenInput()
        self.fields["duration_lower"].widget = forms.HiddenInput()
        self.fields["people_lower"].widget = forms.HiddenInput()
        self.fields["people_upper"].widget = forms.HiddenInput()
        self.fields["description"].required = False
        self.fields["synonyms_keywords"].widget.attrs[
            "placeholder"
        ] = "Please seperate words or phrases with commas."

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

    def save(self, commit=True):
        """Enrich the instance with attribute data, user data and images."""
        self.instance.created_by = self.user
        if not self.image or not self.filters_json:
            raise ValueError("You need to add the filter data and the image.")
        self.instance.attributes = self.filters_json
        super(NewActivityForm, self).save(commit=commit)
        self.instance.images.add(self.image)
