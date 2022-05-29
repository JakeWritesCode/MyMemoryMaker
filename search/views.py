# -*- coding: utf-8 -*-
"""Views for search."""

# 3rd-party
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

# Project
from search.constants import FILTERS
from search.filters import FilterQueryProcessor
from search.filters import FilterSearchForm
from search.filters import FilterSettingForm
from search.forms import NewActivityForm
from search.forms import NewPlaceForm
from search.forms import SearchImageForm


@login_required
def new_activity(request):
    """
    Create a new activity.

    In this view we render three separate forms to look like a single form.
    """
    form = NewActivityForm(user=request.user)
    image_form = SearchImageForm(user=request.user)
    filter_setter_form = FilterSettingForm()

    if request.method == "POST":
        # Validate the image form first.
        image_form = SearchImageForm(request.user, request.POST, request.FILES)
        image_form_valid = image_form.is_valid()

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()

        # Finally, bin the main form and validate.
        form = NewActivityForm(request.user, request.POST)
        if form.is_valid() and image_form_valid:
            # Now the form is valid, pass in the data from the other two forms.
            form.image = image_form.save(commit=True)
            form.filters_json = filter_settings
            # Save the new activity
            form.save(commit=True)
            return render(request, "partials/new-activity-complete.html", status=201)

    return render(
        request,
        "partials/new_activity.html",
        {"form": form, "image_form": image_form, "filter_setter_form": filter_setter_form},
    )


@login_required
def new_place(request):
    """
    Create a new place.

    In this view we render three separate forms to look like a single form.
    """
    form = NewPlaceForm(user=request.user)
    image_form = SearchImageForm(user=request.user)
    filter_setter_form = FilterSettingForm()

    if request.method == "POST":
        # Validate the image form first.
        if request.POST.get("link_url"):
            image_required = False
        image_form = SearchImageForm(request.user, request.POST, request.FILES, image_required=image_required)
        image_form_valid = image_form.is_valid()

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()

        # Finally, bin the main form and validate.
        form = NewPlaceForm(request.user, request.POST)
        if form.is_valid() and image_form_valid:
            # Now the form is valid, pass in the data from the other two forms.
            form.image = image_form.save(commit=True)
            # We've got some supplementary google maps data we want to add to attributes here
            gmaps_data = {
                "rating": form.cleaned_data["google_maps_rating"],
                "address": form.cleaned_data["address"]
            }
            filter_settings["google_maps_data"] = gmaps_data
            form.filters_json = filter_settings
            # Save the new activity
            form.save(commit=True)
            return render(request, "partials/new-place-complete.html", status=201)

    return render(
        request,
        "partials/new_place.html",
        {"form": form, "image_form": image_form, "filter_setter_form": filter_setter_form},
    )


def search_view(request):
    """
    Main search view page. Basically loads the template only.

    Actual results are served by search_results.
    """
    filter_search_form = FilterSearchForm()

    return render(
        request,
        "search_home.html",
        {
            "filter_search_form": filter_search_form,
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "filters_dict": FILTERS,
            "search_results_url": request.build_absolute_uri(reverse("search-results")),
        },
    )


def search_results(request):
    """An async view that returns the search results based on GET params."""
    results = FilterQueryProcessor(request.GET).get_results()
    return render(request, "partials/search_results.html", {"results": results})


@login_required
def new_entity_wizard(request):
    """Base level wizard for adding a new search entity."""
    return render(
        request,
        "new_entity_wizard.html",
        {
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        },
    )
