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


SearchImageFormset = forms.modelformset_factory(
    SearchImage,
    fields=["uploaded_image", "alt_text"],
    extra=1,
    widgets={"uploaded_image": forms.FileInput(attrs={"class": "form-control"}),
             "alt_text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Describe your image content."}),}
)


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
        self.fields["headline"].widget.attrs["placeholder"] = "Give us a one sentence summary of your activity."
        self.fields["price_upper"].widget = forms.HiddenInput()
        self.fields["price_lower"].widget = forms.HiddenInput()
        self.fields["duration_upper"].widget = forms.HiddenInput()
        self.fields["duration_lower"].widget = forms.HiddenInput()

    price_upper = forms.FloatField(label="")
    price_lower = forms.FloatField(label="")
    duration_upper = forms.FloatField(label="")
    duration_lower = forms.FloatField(label="")

    class Meta:  # noqa: D106
        model = Activity
        fields = [
            "headline",
            "description",
            "price_upper",
            "price_lower",
            "duration_upper",
            "duration_lower",
            "images",
        ]
        widgets = {"description": RichTextWidget()}
