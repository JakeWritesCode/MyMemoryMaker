# -*- coding: utf-8 -*-
"""Celery config."""

# 3rd-party
from celery import Celery

app = Celery("my_memory_maker")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Simple debug task."""
    print(f"Request: {self.request!r}")
