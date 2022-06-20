# -*- coding: utf-8 -*-
"""Template tag to check if the given entity is in a users wishlist."""

# 3rd-party
from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()


@register.simple_tag(takes_context=True)
def is_in_users_wishlist(context, entity_type: str, entity_id):
    """Turns a string into a dict."""
    if isinstance(context.request.user, AnonymousUser):
        return False
    if entity_type == "Activity":
        if context.request.user.wishlist_activities.filter(id=entity_id).exists():
            return True
        return False
    if entity_type == "Place":
        if context.request.user.wishlist_places.filter(id=entity_id).exists():
            return True
        return False
    if entity_type == "Event":
        if context.request.user.wishlist_events.filter(id=entity_id).exists():
            return True
        return False
