# -*- coding: utf-8 -*-
"""Views for search."""

# 3rd-party
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

# Project
from search.filters import FilterSettingForm
from search.forms import NewActivityForm
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
            messages.info(
                request,
                "Your activity has been saved and has been added to the "
                "queue for moderation. Please check your submissions screen to "
                "see it's progress.",
            )
            return redirect(reverse("index"))

    return render(
        request,
        "partials/new_activity.html",
        {"form": form, "image_form": image_form, "filter_setter_form": filter_setter_form},
    )


def entity_card_test(request):
    return render(request, "partials/search_entity_test_page.html", {

    })