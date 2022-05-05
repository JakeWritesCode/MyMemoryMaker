# -*- coding: utf-8 -*-
"""
ASGI config for MyMemoryMaker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

# Standard Library
import os

# 3rd-party
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyMemoryMaker.settings")

application = get_asgi_application()
