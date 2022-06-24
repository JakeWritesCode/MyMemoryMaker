"""Base classes for different types of rule."""
# Standard Library
import operator
from functools import reduce
from typing import Union

# 3rd-party
from django.db.models import Q
from django.db.models import QuerySet
from django.utils import timezone

# Project
from integrations.eventbrite import get_or_create_api_user
from search.constants import FLAT_FILTERS
from search.models import Activity
from search.models import Event
from search.models import Place


class BaseRule:
    """A base rule class type."""

    APPLIES_TO = [Activity, Event, Place]
    REQUIRED_FILTERS = []
    MARK_AS_APPROVED = False
    ACTIVITIES_TO_ADD = []

    def _generate_filters(self):
        """A helper function to generate filters, with some additional checks."""
        new_filters = {}
        for req_filter in self.REQUIRED_FILTERS:
            if req_filter not in FLAT_FILTERS:
                raise ValueError(f"Filter {req_filter} not found in filter list.")
            new_filters[req_filter] = True

        return new_filters

    def _add_activities(self, item: Union[Activity, Event, Place]):
        """
        Adds a list of activities by headline to the listing.

        Will fail silently if it can't find the activity.
        """
        if isinstance(item, Activity):
            return
        for activity_headline in self.ACTIVITIES_TO_ADD:
            try:
                activity = Activity.objects.get(headline=activity_headline)
            except Activity.DoesNotExist:
                continue
            item.activities.add(activity)

    def _update(self, item: Union[Activity, Event, Place]):
        """This is the bit where you do whatever you like."""
        if self.MARK_AS_APPROVED:
            item.approval_timestamp = timezone.now()
            item.approved_by = get_or_create_api_user()


class HeadlineDescriptionContainsRule(BaseRule):
    """If the headline or description contains X, apply the following traits."""

    SEARCH_TERMS = []
    UPDATED_FIELDS = []

    def _update(self, item: Union[Activity, Event, Place]):
        """This is the bit where you do whatever you like."""
        if self.MARK_AS_APPROVED:
            item.approval_timestamp = timezone.now()
            item.approved_by = get_or_create_api_user()
            for field in ["approval_timestamp", "approved_by"]:
                if field not in self.UPDATED_FIELDS:
                    self.UPDATED_FIELDS.append(field)

    def apply_single(self, item: Union[Activity, Event, Place]):
        """Apply the rule engine to a single instance."""
        self._update(item)
        item.save()

    def apply(self, qs: QuerySet):
        """Apply the rule."""
        if qs.model not in self.APPLIES_TO:
            return

        filter_terms = [Q(headline__contains=x) for x in self.SEARCH_TERMS]
        filter_terms += [Q(description__contains=x) for x in self.SEARCH_TERMS]
        found = qs.filter(reduce(operator.or_, filter_terms))
        lst = list(found)

        # Can't use update here because we need to append.
        for item in lst:
            self._update(item)
        qs.model.objects.bulk_update(lst, self.UPDATED_FIELDS)
