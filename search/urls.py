# -*- coding: utf-8 -*-
"""Urls for search app."""
# 3rd-party
from django.urls import path

# Local
from . import views

urlpatterns = [
    # Form partials
    path("new-activity", views.new_activity, name="new-activity"),
    path("new-place", views.new_place, name="new-place"),
    path("search-results", views.search_results, name="search-results"),
    # Whole pages
    path("", views.search_view, name="search-home"),
    path("new-submission", views.new_entity_wizard, name="new-submission"),
]
