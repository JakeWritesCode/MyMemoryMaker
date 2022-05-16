# Standard Library
import re

# 3rd-party
from django import template
from django.conf import settings

# Project
from search.filters import format_field_or_category_name

register = template.Library()


def filter_name_human_readable(value):
    """Returns a filter name in human-readable format."""

    return format_field_or_category_name(value)


register.filter("filter_name_human_readable", filter_name_human_readable)
