# -*- coding: utf-8 -*-
"""Base project."""

# Local
from .celery import app as celery_app

__all__ = ("celery_app",)
