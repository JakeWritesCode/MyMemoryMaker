# -*- coding: utf-8 -*-
"""Production settings."""

# Standard Library
import sys
from os import getenv

# 3rd-party
import dj_database_url

# Project
from my_memory_maker.settings.base import *  # noqa: F403 F401

DEBUG = getenv("DEBUG", False)  # noqa: F405
ALLOWED_HOSTS = [getenv("DJANGO_ALLOWED_HOSTS")]
STATIC_URL = "/staticfiles/"

if len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(getenv("DATABASE_URL")),
    }

SEARCH_SHOW_UNMODERATED_RESULTS = {
    "Activity": False,
    "Place": False,
    "Event": True,
}
