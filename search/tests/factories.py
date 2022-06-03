# -*- coding: utf-8 -*-
"""Factories for search models."""

# Standard Library
import random
from datetime import timedelta

# 3rd-party
from django.utils import timezone
from factory import LazyAttribute
from factory import LazyFunction
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

# Project
from search import models
from search.constants import SEARCH_ENTITY_SOURCES
from users.tests.factories import CustomUserFactory

fake = Faker()


class SearchImageFactory(DjangoModelFactory):
    """CustomUser factory."""

    uploaded_by = SubFactory(CustomUserFactory)
    uploaded_timestamp = timezone.now
    uploaded_image = fake.url()
    alt_text = fake.sentence()

    class Meta:  # noqa: D106
        model = models.SearchImage


class ActivityFactory(DjangoModelFactory):
    """Activity factory."""

    created_by = SubFactory(CustomUserFactory)
    # approval not completed by default.
    headline = fake.sentence()
    description = fake.paragraph()

    price_base = LazyFunction(lambda: random.randint(5, 50))
    price_lower = LazyAttribute(lambda o: o.price_base * random.random())
    price_upper = LazyAttribute(lambda o: o.price_base * (1 + random.random()))

    duration_base = LazyFunction(lambda: random.randint(30, 500))
    duration_lower = LazyAttribute(lambda o: o.duration_base * random.random())
    duration_upper = LazyAttribute(lambda o: o.duration_base * (1 + random.random()))

    people_base = LazyFunction(lambda: random.randint(1, 20))
    people_lower = LazyAttribute(lambda o: o.people_base * random.random())
    people_upper = LazyAttribute(lambda o: o.people_base * (1 + random.random()))
    source_type = SEARCH_ENTITY_SOURCES[0]

    # TODO - Build this out...
    attributes = {}

    class Meta:  # noqa: D106
        model = models.Activity
        exclude = ("price_base", "duration_base", "people_base")


class PlaceFactory(DjangoModelFactory):
    """Place factory."""

    created_by = SubFactory(CustomUserFactory)
    # approval not completed by default.
    headline = fake.sentence()
    description = fake.paragraph()

    price_base = LazyFunction(lambda: random.randint(5, 50))
    price_lower = LazyAttribute(lambda o: o.price_base * random.random())
    price_upper = LazyAttribute(lambda o: o.price_base * (1 + random.random()))

    duration_base = LazyFunction(lambda: random.randint(30, 500))
    duration_lower = LazyAttribute(lambda o: o.duration_base * random.random())
    duration_upper = LazyAttribute(lambda o: o.duration_base * (1 + random.random()))

    people_base = LazyFunction(lambda: random.randint(1, 20))
    people_lower = LazyAttribute(lambda o: o.people_base * random.random())
    people_upper = LazyAttribute(lambda o: o.people_base * (1 + random.random()))
    source_type = SEARCH_ENTITY_SOURCES[0]

    location_lat = LazyFunction(lambda: float(fake.latitude()))
    location_long = LazyFunction(lambda: float(fake.longitude()))

    attributes = {"google_maps_data": {"address": "Test address", "rating": 4.1}}

    class Meta:  # noqa: D106
        model = models.Place
        exclude = ("price_base", "duration_base", "people_base")


class EventFactory(DjangoModelFactory):
    """Event factory."""

    created_by = SubFactory(CustomUserFactory)
    # approval not completed by default.
    headline = fake.sentence()
    description = fake.paragraph()

    price_base = LazyFunction(lambda: random.randint(5, 50))
    price_lower = LazyAttribute(lambda o: o.price_base * random.random())
    price_upper = LazyAttribute(lambda o: o.price_base * (1 + random.random()))

    duration_base = LazyFunction(lambda: random.randint(30, 500))
    duration_lower = LazyAttribute(lambda o: o.duration_base * random.random())
    duration_upper = LazyAttribute(lambda o: o.duration_base * (1 + random.random()))

    people_base = LazyFunction(lambda: random.randint(1, 20))
    people_lower = LazyAttribute(lambda o: o.people_base * random.random())
    people_upper = LazyAttribute(lambda o: o.people_base * (1 + random.random()))
    source_type = SEARCH_ENTITY_SOURCES[0]

    # TODO - Build this out...
    attributes = {}

    date_base = LazyFunction(lambda: timezone.now() + timedelta(days=random.randint(5, 50)))
    dates = LazyAttribute(
        lambda o: [
            [
                o.date_base - timedelta(hours=random.randint(1, 4)),
                o.date_base + timedelta(hours=random.randint(1, 4)),
            ],
            [
                o.date_base + timedelta(hours=24) - timedelta(hours=random.randint(1, 4)),
                o.date_base + timedelta(hours=24) + timedelta(hours=random.randint(1, 4)),
            ],
        ],
    )

    class Meta:  # noqa: D106
        model = models.Event
        exclude = ("price_base", "duration_base", "date_base", "people_base")
