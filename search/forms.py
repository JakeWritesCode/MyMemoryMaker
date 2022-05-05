# -*- coding: utf-8 -*-
"""Forms for search."""

# 3rd-party
from django import forms

# Project
from search.models import Activity


def get_activity_choices():
    """Get a list of tuples representing all active activities."""
    choices = [
        (f"{activity.headline} ({', '.join(activity.synonyms)})", activity.id)
        for activity in Activity.objects.filter(approval_timestamp__isnull=False)
    ]
    choices.append(("Create your own...", "create_your_own"))
    return choices


class ActivitySelectorForm(forms.Form):
    """Tag like form allows you to select multiple activities or start creating a new one."""

    activities = forms.MultipleChoiceField(choices=get_activity_choices(), required=True)
