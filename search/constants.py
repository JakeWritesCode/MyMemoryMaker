# -*- coding: utf-8 -*-
"""Constants for the search app."""

SEARCH_ENTITY_SOURCES = ["manually_added", "eventbrite"]

"""Filters configuration"""
FILTERS = {
    "sports": [
        "team_sports",
        "exercise_and_fitness",
        "martial_arts",
        "ball_games",
        "cycling",
        "motorsport",
        "water_sports",
        "winter_sports",
        "other_sports",
    ],
    "arts": ["theatre", "comedy", "cinema_and_film", "concerts", "museums", "other_arts"],
    "hobbies": [
        "arts_and_crafts",
        "music",
        "games",
        "vehicles_and_transport",
        "fashion",
        "home_and_lifestyle",
        "spirituality",
        "science_and_tech",
        "other_hobbies",
    ],
    "music": [
        "alternative",
        "blues_and_jazz",
        "classical",
        "country",
        "electronic",
        "folk",
        "hip_hop_and_rap",
        "indie",
        "metal",
        "pop",
        "rnb",
        "rock",
        "acoustic",
        "punk",
        "other_music",
    ],
    "food_and_drink": [
        "nightlife",
        "restaurants",
        "bars",
        "cafes",
        "pubs",
        "indian",
        "italian",
        "other_european",
        "chinese",
        "greek",
        "thai",
        "british",
        "spanish",
        "japanese",
        "american",
        "mexican",
        "vegan_speciality",
        "vegetarian_speciality",
        "other_food_and_drink",
    ],
    "other_categories": [
        "outdoor",
        "landmarks",
        "culture",
        "social",
        "parenting_and_family",
        "wellbeing",
        "travel",
        "business",
        "charity_and_causes",
        "wedding",
        "festival",
        "educational",
        "seasonal_and_holiday",
        "politics",
        "dating",
        "pets",
    ],
    "venue": [
        "home",
        "inside",
        "outside",
        "dog_friendly",
        "child_friendly",
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
