"""The actual rules."""

# Standard Library
from typing import Union

# Project
from integrations.rule_engine.rule_types import HeadlineDescriptionContainsRule
from search.models import Activity
from search.models import Event
from search.models import Place


class PlaceChurchChapelCathedral(HeadlineDescriptionContainsRule):
    """Headline or description contains church, chapel or cathedral."""

    SEARCH_TERMS = ["church", "chapel", "cathedral", "Church", "Chapel", "Cathedral"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "alone",
        "family",
        "inside",
        "social",
        "wedding",
        "classical",
        "spirituality",
        "child_friendly",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 0
        item.duration_lower = 1
        item.duration_upper = 6
        item.people_lower = 1
        item.people_upper = 100
        item.attributes |= self._generate_filters()

        super(PlaceChurchChapelCathedral, self)._update(item)


class PlacePark(HeadlineDescriptionContainsRule):
    """Headline or description contains park."""

    SEARCH_TERMS = ["park", "Park"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "family",
        "couple",
        "alone",
        "family",
        "outside",
        "outdoor",
        "ball_games",
        "team_sports",
        "exercise_and_fitness",
        "dog_friendly",
        "child_friendly",
    ]
    ACTIVITIES_TO_ADD = [
        "Photography",
        "Go for a walk or hike",
        "Go on a bike ride",
        "Geocaching",
        "Running",
        "Football",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 0
        item.duration_lower = 1
        item.duration_upper = 6
        item.people_lower = 1
        item.people_upper = 20
        item.attributes |= self._generate_filters()
        self._add_activities(item)
        super(PlacePark, self)._update(item)


class PlaceFarm(HeadlineDescriptionContainsRule):
    """Headline or description contains Farm."""

    SEARCH_TERMS = ["farm", "Farm"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "family",
        "outdoor",
        "outside",
        "child_friendly",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 20
        item.duration_lower = 1
        item.duration_upper = 6
        item.people_lower = 1
        item.people_upper = 5
        item.attributes |= self._generate_filters()

        super(PlaceFarm, self)._update(item)


class PlaceExhibitionConvention(HeadlineDescriptionContainsRule):
    """Headline or description contains Exhibition."""

    SEARCH_TERMS = ["Exhibition", "exhibition", "convention", "Convention"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "exercise_and_fitness",
        "cycling",
        "motorsport",
        "other_sports",
        "cinema_and_film",
        "other_arts",
        "arts_and_crafts",
        "music",
        "games",
        "vehicles_and_transport",
        "fashion",
        "home_and_lifestyle",
        "spirituality",
        "science_and_tech",
        "other_hobbies",
        "other_music",
        "other_food_and_drink",
        "culture",
        "social",
        "parenting_and_family",
        "wellbeing",
        "travel",
        "business",
        "charity_and_causes",
        "wedding",
        "seasonal_and_holiday",
        "pets",
        "inside",
        "dog_friendly",
        "friends",
        "couple",
        "alone",
        "family",
        "colleagues",
    ]
    ACTIVITIES_TO_ADD = [
        "Go to an exhibition",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 100
        item.duration_lower = 1
        item.duration_upper = 6
        item.people_lower = 1
        item.people_upper = 15
        item.attributes |= self._generate_filters()
        self._add_activities(item)
        super(PlaceExhibitionConvention, self)._update(item)


class PlaceConference(HeadlineDescriptionContainsRule):
    """Headline or description contains Conference."""

    SEARCH_TERMS = ["conference", "Conference"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "couple",
        "alone",
        "colleagues",
        "business",
        "educationalal",
    ]
    ACTIVITIES_TO_ADD = ["Go to a lecture"]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 500
        item.duration_lower = 4
        item.duration_upper = 72
        item.people_lower = 1
        item.people_upper = 100
        item.attributes |= self._generate_filters()
        self._add_activities(item)

        super(PlaceConference, self)._update(item)


class PlaceHotel(HeadlineDescriptionContainsRule):
    """Headline or description contains Hotel."""

    SEARCH_TERMS = ["hotel", "Hotel"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "bars",
        "friends",
        "couple",
        "alone",
        "family",
        "inside",
        "travel",
        "wellbeing",
        "colleagues",
        "restaurants",
        "business",
        "child_friendly",
    ]
    ACTIVITIES_TO_ADD = ["City Trip"]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 30
        item.price_upper = 500
        item.duration_lower = 6
        item.duration_upper = 72
        item.people_lower = 1
        item.people_upper = 4
        item.attributes |= self._generate_filters()
        self._add_activities(item)

        super(PlaceHotel, self)._update(item)


class PlaceO2(HeadlineDescriptionContainsRule):
    """Headline or description contains O2 (academies and such)."""

    SEARCH_TERMS = ["o2", "O2"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "comedy",
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
        "nightlife",
        "social",
        "inside",
        "child_friendly",
        "friends",
        "couple",
        "alone",
    ]
    ACTIVITIES_TO_ADD = ["Go to a concert", "Go for a night out"]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 100
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()
        self._add_activities(item)

        super(PlaceO2, self)._update(item)


class PlaceGolfClub(HeadlineDescriptionContainsRule):
    """Headline or description contains Golf club."""

    SEARCH_TERMS = ["golf club", "Golf Club", "golf Club", "Golf club"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "ball_games",
        "friends",
        "couple",
        "alone",
        "colleagues",
        "outside",
        "outdoor",
        "other_sports",
        "other_hobbies",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 100
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 4
        item.attributes |= self._generate_filters()

        super(PlaceGolfClub, self)._update(item)


class PlaceCricketClub(HeadlineDescriptionContainsRule):
    """Headline or description contains cricket club."""

    SEARCH_TERMS = ["cricket club", "Cricket Club", "cricket Club", "Cricket club"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "ball_games",
        "friends",
        "couple",
        "alone",
        "colleagues",
        "family",
        "outside",
        "outdoor",
        "team_sports",
        "other_hobbies",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 100
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()

        super(PlaceCricketClub, self)._update(item)


class PlaceRacecourse(HeadlineDescriptionContainsRule):
    """Headline or description contains Racecourse."""

    SEARCH_TERMS = ["Racecourse", "racecourse"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "colleagues",
        "family",
        "outside",
        "inside",
        "child_friendly",
        "landmarks",
        "charity_and_causes",
        "educationalal",
        "other_sports",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 500
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()

        super(PlaceRacecourse, self)._update(item)


class PlaceTownHall(HeadlineDescriptionContainsRule):
    """Headline or description contains Town Hall."""

    SEARCH_TERMS = ["Town Hall", "Town hall", "town hall", "town Hall"]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "colleagues",
        "family",
        "inside",
        "child_friendly",
        "landmarks",
        "charity_and_causes",
        "educational",
        "politics",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 100
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()

        super(PlaceTownHall, self)._update(item)


class PlaceCommunityCentre(HeadlineDescriptionContainsRule):
    """Headline or description contains Community Center."""

    SEARCH_TERMS = [
        "Community Center",
        "Community center",
        "community Center",
        "community center",
        "Community Centre",
        "Community centre",
        "community Centre",
        "community centre",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "family",
        "alone",
        "inside",
        "child_friendly",
        "educational",
        "landmarks",
        "charity_and_causes",
        "educational",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 250
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()

        super(PlaceCommunityCentre, self)._update(item)


class PlaceTheatre(HeadlineDescriptionContainsRule):
    """Headline or description contains theatre."""

    SEARCH_TERMS = [
        "Theatre",
        "theatre",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "family",
        "alone",
        "inside",
        "child_friendly",
        "educational",
        "theatre",
        "comedy",
        "culture",
        "social",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 10
        item.price_upper = 500
        item.duration_lower = 1
        item.duration_upper = 4
        item.people_lower = 1
        item.people_upper = 5
        item.attributes |= self._generate_filters()

        super(PlaceTheatre, self)._update(item)


class PlaceLibrary(HeadlineDescriptionContainsRule):
    """Headline or description contains Library."""

    SEARCH_TERMS = [
        "library",
        "Library",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "friends",
        "couple",
        "family",
        "alone",
        "inside",
        "child_friendly",
        "educational",
        "social",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 20
        item.duration_lower = 1
        item.duration_upper = 3
        item.people_lower = 1
        item.people_upper = 4
        item.attributes |= self._generate_filters()

        super(PlaceLibrary, self)._update(item)


class PlaceUniversityCollege(HeadlineDescriptionContainsRule):
    """Headline or description contains University / College."""

    SEARCH_TERMS = [
        "University",
        "College",
        "university",
        "college",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "alone",
        "inside",
        "educational",
        "business",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 500
        item.duration_lower = 1
        item.duration_upper = 8
        item.people_lower = 1
        item.people_upper = 1
        item.attributes |= self._generate_filters()

        super(PlaceUniversityCollege, self)._update(item)


class PlaceLeisureCenterFitnessClub(HeadlineDescriptionContainsRule):
    """Headline or description contains Leisure center / fitness club."""

    SEARCH_TERMS = [
        "Leisure Center",
        "Leisure center",
        "leisure Center",
        "leisure center",
        "Leisure Centre",
        "Leisure centre",
        "leisure Centre",
        "leisure centre",
        "Fitness Club",
        "Fitness club",
        "fitness Club",
        "fitness flub",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "alone",
        "family",
        "friends",
        "inside",
        "outside",
        "ball_games",
        "team_sports",
        "exercise_and_fitness",
        "other_sports",
        "child_friendly",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 5
        item.price_upper = 50
        item.duration_lower = 1
        item.duration_upper = 6
        item.people_lower = 1
        item.people_upper = 8
        item.attributes |= self._generate_filters()

        super(PlaceLeisureCenterFitnessClub, self)._update(item)


class PlaceMuseum(HeadlineDescriptionContainsRule):
    """Headline or description contains Museum."""

    SEARCH_TERMS = [
        "museum",
        "Museum",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "museums",
        "alone",
        "friends",
        "family",
        "couple",
        "inside",
        "educational",
        "child_friendly",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 30
        item.duration_lower = 1
        item.duration_upper = 3
        item.people_lower = 1
        item.people_upper = 4
        item.attributes |= self._generate_filters()

        super(PlaceMuseum, self)._update(item)


class PlaceArtGallery(HeadlineDescriptionContainsRule):
    """Headline or description contains Art Gallery."""

    SEARCH_TERMS = [
        "Art Gallery",
        "Art gallery",
        "art Gallery",
        "art gallery",
    ]
    APPLIES_TO = [Place]
    UPDATED_FIELDS = [
        "price_lower",
        "price_upper",
        "duration_lower",
        "duration_upper",
        "people_lower",
        "people_lower",
        "people_upper",
        "attributes",
    ]
    MARK_AS_APPROVED = True
    REQUIRED_FILTERS = [
        "museums",
        "other_arts",
        "arts_and_crafts",
        "alone",
        "family",
        "couple",
        "friends",
        "inside",
        "educational",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.price_lower = 0
        item.price_upper = 30
        item.duration_lower = 1
        item.duration_upper = 3
        item.people_lower = 1
        item.people_upper = 10
        item.attributes |= self._generate_filters()

        super(PlaceArtGallery, self)._update(item)


class EventPlaceFamily(HeadlineDescriptionContainsRule):
    """Headline or description contains family, family friendly."""

    SEARCH_TERMS = [
        "Family",
        "family",
        "Family Friendly",
        "family Friendly",
        "Family friendly",
        "family friendly",
    ]
    APPLIES_TO = [Event, Place]
    UPDATED_FIELDS = [
        "attributes",
    ]
    MARK_AS_APPROVED = False
    REQUIRED_FILTERS = [
        "child_friendly",
        "family",
        "friends",
        "couple",
        "parenting_and_family",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.attributes |= self._generate_filters()

        super(EventPlaceFamily, self)._update(item)


class EventPlaceOutdoor(HeadlineDescriptionContainsRule):
    """Headline or description contains outdoor, outdoors."""

    SEARCH_TERMS = [
        "outdoor",
        "outdoors",
        "Outdoor",
        "Outdoors",
    ]
    APPLIES_TO = [Event, Place]
    UPDATED_FIELDS = [
        "attributes",
    ]
    MARK_AS_APPROVED = False
    REQUIRED_FILTERS = [
        "outside",
        "outdoor",
    ]

    def _update(self, item: Union[Activity, Event, Place]):
        """Update model fields."""
        item.attributes |= self._generate_filters()

        super(EventPlaceOutdoor, self)._update(item)
