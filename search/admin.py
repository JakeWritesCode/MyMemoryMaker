# -*- coding: utf-8 -*-
"""Admin for search."""
# 3rd-party
from django.contrib import admin

# Project
from search import models

admin.site.register(models.SearchImage)
admin.site.register(models.Activity)
admin.site.register(models.Place)
admin.site.register(models.Event)
