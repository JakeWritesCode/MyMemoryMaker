# -*- coding: utf-8 -*-
"""Views for search."""

from django.shortcuts import render
from search.forms import ActivitySelectorForm

def multi_activity_selector(request):
    """A mini view allowing the user to select one or more activities."""
    form = ActivitySelectorForm()
