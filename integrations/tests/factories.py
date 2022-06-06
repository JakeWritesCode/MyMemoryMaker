# -*- coding: utf-8 -*-
"""Factories for integration models."""
# Standard Library
import json
import pathlib
from random import randint

# 3rd-party
from factory import LazyFunction
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

# Project
from integrations import models

fake = Faker()


class EventBriteEventIDFactory(DjangoModelFactory):
    """EventBriteEventID factory."""

    event_id = LazyFunction(lambda: randint(9999999999, 999999999999))

    class Meta:  # noqa: D106
        model = models.EventBriteEventID


class EventBriteRawEventDataFactory(DjangoModelFactory):
    """EventBriteRawEventData factory."""

    event_id = SubFactory(EventBriteEventIDFactory)
    file = pathlib.Path(__file__).parent.resolve()
    with open(f"{file}/mock_api_data/eventbrite_event_data.json", "r") as sample_return:
        data = json.load(sample_return)

    class Meta:  # noqa: D106
        model = models.EventBriteRawEventData
        exclude = ["file", "sample_return"]
