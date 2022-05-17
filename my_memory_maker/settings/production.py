# -*- coding: utf-8 -*-
"""Production settings."""

# 3rd-party
import dj_database_url
from base import *  # noqa: F403

DEBUG = getenv("DEBUG", False)  # noqa: F405
ALLOWED_HOSTS = ["*"]

DATABASES = {"default": dj_database_url.parse(getenv("DATABASE_URL"))}
