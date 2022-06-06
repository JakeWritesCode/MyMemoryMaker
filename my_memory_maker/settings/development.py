# -*- coding: utf-8 -*-
"""Development settings."""

# 3rd-party
import dj_database_url

# Local
from .base import *  # noqa: F403

DEBUG = getenv("DEBUG", True)  # noqa: F405
ALLOWED_HOSTS = ["*"]
STATIC_ROOT = None