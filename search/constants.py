# -*- coding: utf-8 -*-
"""Constants for the search app."""

SEARCH_ENTITY_SOURCES = [
    "manually_added",
]

"""Filters configuration"""
FILTERS = {
    "categories": [
        "nightlife",
        "museums",
        "concerts",
        "sports",
        "arts",
        "food_and_drink",
        "landmarks",
        "cinema_theatre_comedy",
        "outdoors",
        "culture",
        "hobbies",
        "social",
        "parenting_and_family",
    ],
    "venue": [
        "home",
        "inside",
        "outside",
        "dog_friendly",
        "child_friendly",
        "vegan_friendly",
        "vegetarian_friendly",
    ],
    "people": [
        "friends",
        "couple",
        "alone",
        "family",
        "colleagues",
    ],
}

"""
These are the upper and lower bounds we'll allow the user to enter when
creating a new search entity.
"""
GT_LT_FILTERS_UPPER_LOWER_BOUNDS = {
    "duration": [0, 48],  # Hours
    "price": [0, 250],  # Pounds
    "people": [1, 50],
}
