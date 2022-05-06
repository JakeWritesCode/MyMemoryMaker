# -*- coding: utf-8 -*-
"""Models for search."""
# Standard Library
import uuid

# 3rd-party
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import ValidationError
from django.db import models

# Project
from search.constants import SEARCH_ENTITY_SOURCES
from users.models import CustomUser


class SearchImage(models.Model):
    """
    Images uploaded or linked that are related to search entities.

    Images can either be uploaded directly to the site and stored in S3 or be a web URL linked
    from another source (e.g. Google maps).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_timestamp = models.DateTimeField(auto_now=True)
    s3_key = models.CharField(max_length=2048, null=True)
    link_url = models.CharField(max_length=2048, null=True)
    alt_text = models.CharField(max_length=2048)

    def __str__(self):
        """String representation."""
        return f"Search Uploaded Image {self.id}: {self.alt_text}"

    def clean(self):
        """Custom model validation."""
        super(SearchImage, self).clean()

        # Either S3 key or link URL must be filled in.
        if not self.s3_key and not self.link_url:
            raise ValidationError("You must either specify an s3 key or link url.")


class SearchEntity(models.Model):
    """An abstract base class for searchable entities."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
    )
    creation_timestamp = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="%(class)s_approved_by",
        null=True,
    )
    approval_timestamp = models.DateTimeField(null=True)
    headline = models.CharField(max_length=2048)
    description = models.TextField()
    price_lower = models.FloatField()
    price_upper = models.FloatField()
    duration_lower = models.IntegerField()
    duration_upper = models.IntegerField()
    source_type = models.CharField(
        max_length=256,
        choices=[(choice, choice) for choice in SEARCH_ENTITY_SOURCES],
        verbose_name="Source of entity.",
    )
    source_id = models.UUIDField(
        verbose_name="Pseudo-FK to the source data table (if any)",
        null=True,
    )
    images = models.ManyToManyField(SearchImage)
    attributes = HStoreField()

    class Meta:  # noqa: D106
        abstract = True


class Activity(SearchEntity):
    """Something to do, without a specific date or place."""

    synonyms = ArrayField(models.CharField(max_length=1024), null=True, blank=True)

    def __str__(self):
        """String representation."""
        return f"Activity: {self.headline}"


class Place(SearchEntity):
    """Place - A place where users can either do an activity or attend an event."""

    google_maps_place_id = models.CharField(max_length=1024, null=True)
    activities = models.ManyToManyField(Activity)

    def __str__(self):
        """String representation."""
        return f"Place: {self.headline}"


class Event(SearchEntity):
    """A specific instance of an activity that will take place in a given place at a given time."""

    dates = ArrayField(ArrayField(models.DateTimeField(), size=2), verbose_name="Event dates")
    activities = models.ManyToManyField(Activity)
    places = models.ManyToManyField(Place)

    def __str__(self):
        """String representation."""
        return f"Event: {self.headline}"
