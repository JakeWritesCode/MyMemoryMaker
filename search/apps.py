# -*- coding: utf-8 -*-
"""AppConfig for search."""

# 3rd-party
from django.apps import AppConfig


class SearchConfig(AppConfig):
    """App config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
