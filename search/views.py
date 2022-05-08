# -*- coding: utf-8 -*-
"""Views for search."""

# 3rd-party
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Project
from search.filters import FilterSettingForm
from search.forms import ActivitySelectorForm
from search.forms import NewActivityForm
from search.forms import SearchImageForm
from search.models import SearchImage


def multi_activity_selector(request):
    """A mini view allowing the user to select one or more activities."""
    form = ActivitySelectorForm()


@login_required
def new_activity(request):
    """Create a new activity."""

    form = NewActivityForm(user=request.user)
    image_form = SearchImageForm(user=request.user)
    filter_setter_form = FilterSettingForm()

    return render(
        request,
        "partials/new_activity.html",
        {"form": form,
         "image_form": image_form,
         "filter_setter_form": filter_setter_form},
    )
