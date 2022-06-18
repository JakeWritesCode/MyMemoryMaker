# -*- coding: utf-8 -*-
"""Views for search."""

# Standard Library
from ast import literal_eval
from http.client import NOT_FOUND

# 3rd-party
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

# Project
from search.constants import FILTERS
from search.filters import FilterQueryProcessor
from search.filters import FilterSearchForm
from search.filters import FilterSettingForm
from search.forms import EventDatesForm
from search.forms import NewActivityForm
from search.forms import NewEventForm
from search.forms import NewPlaceForm
from search.forms import SearchImageForm
from search.models import Activity, SearchImage
from search.models import Event
from search.models import Place


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
        {
            "form": form,
            "image_form": image_form,
            "filter_setter_form": filter_setter_form,
            "partial_target": reverse(new_activity),
        },
    )


@login_required
@staff_member_required
def edit_activity(request, activity_id: str):
    """
    Edit an existing activity.

    In this view we render three separate forms to look like a single form.
    """
    activity = get_object_or_404(Activity, id=activity_id)
    image = activity.images.first()
    filters = {}
    for key, val in activity.attributes.items():
        filters[key] = True if val == "True" else False

    form = NewActivityForm(user=request.user, instance=activity)
    image_form = SearchImageForm(user=request.user, instance=image, image_required=False)
    filter_setter_form = FilterSettingForm(initial=filters)

    if request.method == "POST":
        # Validate the image form first.
        image_form = SearchImageForm(
            request.user,
            request.POST,
            request.FILES,
            image_required=False,
        )
        image_form.is_valid()
        # Manually update each image attribute individually.
        for attr in ["link_url", "uploaded_image", "alt_text"]:
            if image_form.cleaned_data[attr]:
                setattr(image, attr, image_form.cleaned_data[attr])

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()

        # Finally, bind the main form and validate.
        form = NewActivityForm(request.user, request.POST, instance=activity)
        if form.is_valid():
            image.save()
            form.image = image
            form.filters_json = filter_settings
            activity.approval_timestamp = timezone.now()
            activity.approved_by = request.user
            # Save the activity
            form.save(commit=True)
            return render(request, "partials/new-activity-complete.html", status=200)

    return render(
        request,
        "edit_search_entity.html",
        {
            "form": form,
            "image_form": image_form,
            "filter_setter_form": filter_setter_form,
            "entity_type": "Activity",
            "partial_target": reverse(edit_activity, args=[activity.id]),
            "entity_id": activity_id,
        },
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
        else:
            image_required = True
        image_form = SearchImageForm(
            request.user,
            request.POST,
            request.FILES,
            image_required=image_required,
        )
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
                "address": form.cleaned_data["address"],
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


@login_required
@staff_member_required
def edit_place(request, place_id: str):
    """
    Edit an existing place.

    In this view we render three separate forms to look like a single form.
    """
    template = "edit_search_entity.html"
    place = get_object_or_404(Place, id=place_id)
    image = place.images.first()
    if not image:
        image = SearchImage(uploaded_by=request.user)
    filters = {}
    for key, val in place.attributes.items():
        filters[key] = True if val == "True" else False
    gmaps_data = literal_eval(place.attributes["google_maps_data"])
    gmaps_initial = {"google_maps_rating": gmaps_data["rating"], "address": gmaps_data["address"]}

    form = NewPlaceForm(user=request.user, instance=place, initial=gmaps_initial)
    image_form = SearchImageForm(user=request.user, instance=image, image_required=False)
    filter_setter_form = FilterSettingForm(initial=filters)

    if request.method == "POST":
        # Validate the image form first.
        template = "partials/new_place.html"
        if request.POST.get("link_url"):
            image_required = False
        else:
            image_required = True
        image_form = SearchImageForm(
            request.user,
            request.POST,
            request.FILES,
            image_required=image_required,
        )
        image_form.is_valid()

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()
        # Manually update each image attribute individually.
        for attr in ["link_url", "uploaded_image", "alt_text"]:
            try:
                if image_form.cleaned_data[attr]:
                    setattr(image, attr, image_form.cleaned_data[attr])
            except KeyError:
                continue

        # Finally, bin the main form and validate.
        form = NewPlaceForm(request.user, request.POST, instance=place)
        if form.is_valid():
            image.save()
            # Now the form is valid, pass in the data from the other two forms.
            # We've got some supplementary google maps data we want to add to attributes here
            gmaps_data = {
                "rating": form.cleaned_data["google_maps_rating"],
                "address": form.cleaned_data["address"],
            }
            filter_settings["google_maps_data"] = gmaps_data
            form.filters_json = filter_settings
            form.image = image
            # Save the place
            place.approval_timestamp = timezone.now()
            place.approved_by = request.user
            form.save(commit=True)
            return render(request, "partials/new-place-complete.html", status=200)

    return render(
        request,
        template,
        {
            "form": form,
            "image_form": image_form,
            "filter_setter_form": filter_setter_form,
            "entity_type": "Place",
            "partial_target": reverse(edit_place, args=[place.id]),
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "entity_id": place_id,
        },
    )


@login_required
def new_event(request):
    """
    Create a new event.

    In this view we render three separate forms to look like a single form.
    """
    form = NewEventForm(user=request.user)
    image_form = SearchImageForm(user=request.user)
    event_dates_form = EventDatesForm()
    filter_setter_form = FilterSettingForm()

    if request.method == "POST":
        # Validate the image form first.
        image_form = SearchImageForm(request.user, request.POST, request.FILES)
        image_form_valid = image_form.is_valid()

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()

        # Next, check the event dates
        event_dates_form = EventDatesForm(request.POST)
        dates_form_valid = event_dates_form.is_valid()

        # Finally, bin the main form and validate.
        form = NewEventForm(request.user, request.POST)
        if form.is_valid() and image_form_valid and dates_form_valid:
            # Now the form is valid, pass in the data from the other two forms.
            form.image = image_form.save(commit=True)
            form.filters_json = filter_settings
            form.event_dates = [
                (
                    event_dates_form.cleaned_data["from_date"],
                    event_dates_form.cleaned_data["to_date"],
                ),
            ]
            # Save the new activity
            form.save(commit=True)
            return render(request, "partials/new-event-complete.html", status=201)

    return render(
        request,
        "partials/new_event.html",
        {
            "form": form,
            "image_form": image_form,
            "filter_setter_form": filter_setter_form,
            "event_dates_form": event_dates_form,
        },
    )


@login_required
@staff_member_required
def edit_event(request, event_id: str):
    """
    Edit an existing event.

    In this view we render three separate forms to look like a single form.
    """
    template = "edit_search_entity.html"
    event = get_object_or_404(Event, id=event_id)
    form = NewEventForm(user=request.user, instance=event)

    image = event.images.first()
    image_form = SearchImageForm(user=request.user, instance=image, image_required=False)

    filters = {}
    for key, val in event.attributes.items():
        filters[key] = True if val == "True" else False
    filter_setter_form = FilterSettingForm(initial=filters)

    dates_initial = {"from_date": event.dates[0][0], "to_date": event.dates[0][1]}
    event_dates_form = EventDatesForm(initial=dates_initial)

    if request.method == "POST":
        # Validate the image form first.
        template = "partials/new_event.html"
        image_form = SearchImageForm(
            request.user,
            request.POST,
            request.FILES,
            image_required=False,
        )
        image_form.is_valid()

        # Then bind the filters form, and parse the results to JSON.
        filter_setter_form = FilterSettingForm(request.POST)
        filter_settings = filter_setter_form.save()
        event_dates_form = EventDatesForm(request.POST)
        dates_form_valid = event_dates_form.is_valid()
        # Manually update each image attribute individually.
        for attr in ["link_url", "uploaded_image", "alt_text"]:
            if image_form.cleaned_data[attr]:
                setattr(image, attr, image_form.cleaned_data[attr])

        # Finally, bind the main form and validate.
        form = NewEventForm(request.user, request.POST, instance=event)
        if form.is_valid() and dates_form_valid:
            image.save()
            form.filters_json = filter_settings
            form.image = image
            form.event_dates = [
                (
                    event_dates_form.cleaned_data["from_date"],
                    event_dates_form.cleaned_data["to_date"],
                ),
            ]
            # Save the event
            event.approved_by = request.user
            event.approval_timestamp = timezone.now()
            form.save(commit=True)
            return render(request, "partials/new-event-complete.html", status=200)

    return render(
        request,
        template,
        {
            "form": form,
            "image_form": image_form,
            "filter_setter_form": filter_setter_form,
            "event_dates_form": event_dates_form,
            "entity_type": "Event",
            "partial_target": reverse(edit_event, args=[event.id]),
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "entity_id": event_id,
        },
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


def see_more(request, entity_type, entity_id):
    """The detail page of a given card. Show details for the entity and other related entities."""
    available_types = [["Activity", Activity], ["Event", Event], ["Place", Place]]
    if entity_type not in [x[0] for x in available_types]:
        return HttpResponse("The entity type you requested does not exist.", status=NOT_FOUND)
    entity = [x[1] for x in available_types if entity_type == x[0]][0]
    try:
        entity_instance = entity.objects.get(id=entity_id)
    except (Activity.DoesNotExist, Place.DoesNotExist, Event.DoesNotExist):
        return HttpResponse("The entity ID you requested does not exist.", status=NOT_FOUND)

    return render(
        request,
        "see_more.html",
        {"search_entity": entity_instance, "entity_type": entity_type},
    )
