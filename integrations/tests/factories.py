# -*- coding: utf-8 -*-
"""Factories for integration models."""
# Standard Library
from random import randint

# 3rd-party
from factory import LazyAttribute
from factory import LazyFunction
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
