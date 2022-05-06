# -*- coding: utf-8 -*-
"""Views for search."""

# 3rd-party
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from search.models import SearchImage

# Project
from search.forms import ActivitySelectorForm
from search.forms import NewActivityForm
from search.forms import SearchImageFormset


def multi_activity_selector(request):
    """A mini view allowing the user to select one or more activities."""
    form = ActivitySelectorForm()


@login_required
def new_activity(request):
    """Create a new activity."""

    form = NewActivityForm(user=request.user)
    images_formset = SearchImageFormset(queryset=SearchImage.objects.none())

    return render(
        request, "partials/new_activity.html", {"form": form, "images_formset": images_formset}
    )
