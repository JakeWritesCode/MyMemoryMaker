# -*- coding: utf-8 -*-
"""Admin for search."""
# 3rd-party
from django.contrib import admin

# Project
from search import models

admin.register(models.SearchImages)
admin.register(models.Activity)
admin.register(models.Place)
admin.register(models.Event)
