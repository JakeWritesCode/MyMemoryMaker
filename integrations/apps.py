# -*- coding: utf-8 -*-
"""Admin for integrations."""
# 3rd-party
from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """App config.  """

    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"
