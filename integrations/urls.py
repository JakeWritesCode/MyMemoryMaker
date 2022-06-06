# -*- coding: utf-8 -*-
"""Integrations URLs."""

# 3rd-party
from django.urls import path

# Local
from . import views

urlpatterns = [
    # Form partials
    path(
        "get_eventbrite_event_ids", views.get_eventbrite_event_ids, name="get_eventbrite_event_ids",
    ),
    path(
        "get_eventbrite_raw_event_data",
        views.get_eventbrite_raw_event_data,
        name="get_eventbrite_raw_event_data",
    ),
    path(
        "parse_eventbrite_data_into_events",
        views.parse_eventbrite_data_into_events,
        name="parse_eventbrite_data_into_events",
    ),
    path("start_eventbrite_async_download",
         views.start_eventbrite_async_download,
         name="start_eventbrite_async_download"
    ),
]
