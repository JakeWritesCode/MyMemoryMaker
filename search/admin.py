# -*- coding: utf-8 -*-
"""Admin for search."""
# 3rd-party
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Project
from search import models


class ActivityAdmin(admin.ModelAdmin):
    """Launch and editor window for that entity type."""

    list_display = ["headline", "source_type", "created_by", "approved_by", "edit_in_wizard"]

    def edit_in_wizard(self, obj):
        """Generate and editor window."""
        url = reverse("edit-activity", args=[obj.id])
        return format_html(f'<a class="button" href="{url}">Edit in Wizard</a>')


admin.site.register(models.SearchImage)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.Place)
admin.site.register(models.Event)
