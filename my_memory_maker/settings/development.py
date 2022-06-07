# -*- coding: utf-8 -*-
"""Development settings."""

# 3rd-party
import dj_database_url

# Local
from .base import *  # noqa: F403

DEBUG = getenv("DEBUG", True)  # noqa: F405
ALLOWED_HOSTS = ["*"]
STATIC_ROOT = None

DATABASES = {
    "default": dj_database_url.parse("postgresql://doadmin:AVNS_AW0UEzmFaKtIx-U@app-1de665e8-4f71-4365-9168-89fe0e26bcd0-do-user-11049784-0.b.db.ondigitalocean.com:25060/my-memory-maker?sslmode=require"),
}