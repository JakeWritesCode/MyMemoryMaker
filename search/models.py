# -*- coding: utf-8 -*-
"""Models for search."""
# Standard Library
import uuid

# 3rd-party
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import ValidationError
from django.db import models
from geopy.distance import distance

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
    uploaded_image = models.ImageField(null=True, upload_to="searchimages/")
    link_url = models.CharField(max_length=2048, null=True, blank=True)
    alt_text = models.CharField(max_length=2048)

    def __str__(self):
        """String representation."""
        return f"Search Uploaded Image {self.id}: {self.alt_text}"

    @property
    def display_url(self):
        """Either the uploaded url or the link url, depending on which is filled in."""
        return self.uploaded_image.url if self.uploaded_image else self.link_url

    def clean(self):
        """Custom model validation."""
        super(SearchImage, self).clean()

        # Either S3 key or link URL must be filled in.
        if not self.uploaded_image and not self.link_url:
            raise ValidationError("You must either add an uploaded image or specify an S3 URL.")

    def save(self, *args, **kwargs):
        """Call the clean method on save."""
        self.clean()
        return super(SearchImage, self).save(*args, **kwargs)


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
        blank=True,
    )
    approval_timestamp = models.DateTimeField(null=True, blank=True)
    headline = models.CharField(max_length=2048)
    description = models.TextField()
    price_lower = models.FloatField()
    price_upper = models.FloatField()
    duration_lower = models.IntegerField()
    duration_upper = models.IntegerField()
    people_lower = models.IntegerField()
    people_upper = models.IntegerField()
    synonyms_keywords = ArrayField(models.CharField(max_length=1024), null=True, blank=True)
    source_type = models.CharField(
        max_length=256,
        choices=[(choice, choice) for choice in SEARCH_ENTITY_SOURCES],
        verbose_name="Source of entity.",
    )
    source_id = models.UUIDField(
        verbose_name="Pseudo-FK to the source data table (if any)",
        null=True,
        blank=True,
    )
    images = models.ManyToManyField(SearchImage)
    attributes = HStoreField()

    class Meta:  # noqa: D106
        abstract = True

    def clean_synonyms_keywords(self):
        """Make all synonyms lower case."""
        if self.synonyms_keywords:
            self.synonyms_keywords = [x.lower() for x in self.synonyms_keywords]

    def save(self, **kwargs):
        """Call clean method on save."""
        self.clean_synonyms_keywords()
        super(SearchEntity, self).save(**kwargs)

    @property
    def active_filters(self):
        """Returns the list of active filters as strings."""
        return [
            filter_name
            for filter_name in self.attributes.keys()
            if self.attributes[filter_name] == "True"
        ]


class Activity(SearchEntity):
    """Something to do, without a specific date or place."""

    def __str__(self):
        """String representation."""
        return f"Activity: {self.headline}"


class Place(SearchEntity):
    """Place - A place where users can either do an activity or attend an event."""

    google_maps_place_id = models.CharField(max_length=1024, null=True)
    location_lat = models.FloatField(null=True, max_length=40)
    location_long = models.FloatField(null=True, max_length=40)
    activities = models.ManyToManyField(Activity)

    def __str__(self):
        """String representation."""
        return f"Place: {self.headline}"

    def distance_from(self, from_lat, from_long):
        """Calculate the distance between this place and some other long / lat point."""
        if not self.location_lat or not self.location_long:
            raise ValueError("We don't know where this place is!")
        return distance((self.location_lat, self.location_long), (from_lat, from_long)).miles


class Event(SearchEntity):
    """A specific instance of an activity that will take place in a given place at a given time."""

    dates = ArrayField(ArrayField(models.DateTimeField(), size=2), verbose_name="Event dates")
    activities = models.ManyToManyField(Activity)
    places = models.ManyToManyField(Place)

    def __str__(self):
        """String representation."""
        return f"Event: {self.headline}"
