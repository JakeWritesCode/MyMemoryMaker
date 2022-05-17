# -*- coding: utf-8 -*-
"""Production settings."""

# 3rd-party
import sys

import dj_database_url
from my_memory_maker.settings.base import *  # noqa: F403

DEBUG = getenv("DEBUG", False)  # noqa: F405
ALLOWED_HOSTS = [getenv("DJANGO_ALLOWED_HOSTS")]

if len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(getenv("DATABASE_URL")),
    }