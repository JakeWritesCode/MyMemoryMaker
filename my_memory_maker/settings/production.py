# -*- coding: utf-8 -*-
"""Production settings."""

# 3rd-party
import dj_database_url
from my_memory_maker.settings.base import *  # noqa: F403

DEBUG = getenv("DEBUG", False)  # noqa: F405
ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS")
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = (BASE_DIR / "search/static/", BASE_DIR / "static")

# DATABASES = {"default": dj_database_url.parse(getenv("DATABASE_URL"))}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}