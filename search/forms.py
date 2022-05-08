# -*- coding: utf-8 -*-
"""Forms for search."""

# 3rd-party
from django import forms
from django.contrib.auth.models import AnonymousUser
from djrichtextfield.models import RichTextWidget

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
        required=True, label="Please confirm you have permission to use and share this image."
    )

    def __init__(self, user, *args, **kwargs):  # noqa: D102
        self.user = user
        super(SearchImageForm, self).__init__(*args, **kwargs)
        self.fields["uploaded_image"].widget.attrs["class"] = "form-control"
        self.fields["alt_text"].widget.attrs["placeholder"] = "Please describe your image."

    class Meta:  # noqa: D106
        model = SearchImage
        fields = ["uploaded_image", "alt_text"]


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
            "images",
        ]
        widgets = {"description": RichTextWidget()}
