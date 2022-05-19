# -*- coding: utf-8 -*-
"""Urls for search app."""
# 3rd-party
from django.urls import path

# Local
from . import views

urlpatterns = [
    # Form partials
    path("new-activity", views.new_activity, name="new-activity"),
    path("search-results", views.search_results, name="search-results"),
    # Whole pages
    path("", views.search_view, name="search-home"),
]
