# -*- coding: utf-8 -*-
"""Admin for search."""
# 3rd-party
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Project
from search import models


class SearchEntityAdmin(admin.ModelAdmin):
    """Launch and editor window for that entity type."""

    reverse_func = None
    list_display = ["headline", "source_type", "created_by", "approved_by", "edit_in_wizard"]

    def edit_in_wizard(self, obj):
        """Generate and editor window."""
        url = reverse(self.reverse_func, args=[obj.id])
        return format_html(f'<a class="button" href="{url}">Edit in Wizard</a>')


class ActivityAdmin(SearchEntityAdmin):
    """Activity admin."""

    reverse_func = "edit-activity"


class PlaceAdmin(SearchEntityAdmin):
    """Place admin."""

    reverse_func = "edit-place"


class EventAdmin(SearchEntityAdmin):
    """Event admin."""

    reverse_func = "edit-event"


admin.site.register(models.SearchImage)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.Place, PlaceAdmin)
admin.site.register(models.Event)
