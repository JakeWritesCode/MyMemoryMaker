# -*- coding: utf-8 -*-
"""Admin for integrations."""

# 3rd-party
from django.contrib import admin

# Project
from integrations import models

# Register your models here.
admin.site.register(models.EventBriteEventID)
admin.site.register(models.EventBriteRawEventData)
