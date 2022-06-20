# -*- coding: utf-8 -*-
"""Urls for search app."""
# 3rd-party
from django.urls import path

# Local
from . import views

urlpatterns = [
    # Form partials
    path("new-activity", views.new_activity, name="new-activity"),
    path("edit-activity/<activity_id>", views.edit_activity, name="edit-activity"),
    path("new-place", views.new_place, name="new-place"),
    path("edit-place/<place_id>", views.edit_place, name="edit-place"),
    path("new-event", views.new_event, name="new-event"),
    path("edit-event/<event_id>", views.edit_event, name="edit-event"),
    path("search-results", views.search_results, name="search-results"),
    path("my-wishlist-results", views.my_wishlist_results, name="my-wishlist-results"),
    # Whole pages
    path("", views.search_view, name="search-home"),
    path("new-submission", views.new_entity_wizard, name="new-submission"),
    path("see-more/<entity_type>/<entity_id>", views.see_more, name="see-more"),
    path("my-wishlist", views.my_wishlist, name="my-wishlist"),
    # POST views
    path(
        "modify-wishlist/<entity_type>/<entity_id>/<add_or_remove>",
        views.modify_wishlist,
        name="modify-wishlist",
    ),
]
