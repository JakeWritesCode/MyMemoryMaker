# -*- coding: utf-8 -*-
"""Development settings."""


# Local
import dj_database_url

from .base import *  # noqa: F403

DEBUG = getenv("DEBUG", True)  # noqa: F405
ALLOWED_HOSTS = ["*"]
STATIC_ROOT = None

SEARCH_SHOW_UNMODERATED_RESULTS = True
CELERY_ALWAYS_EAGER = 1
