"""The rule engine is designed to automate some of the workload of moderating."""
# Project
from integrations.rule_engine.rules import EventPlaceFamily
from integrations.rule_engine.rules import EventPlaceOutdoor
from integrations.rule_engine.rules import PlaceArtGallery
from integrations.rule_engine.rules import PlaceChurchChapelCathedral
from integrations.rule_engine.rules import PlaceCommunityCentre
from integrations.rule_engine.rules import PlaceConference
from integrations.rule_engine.rules import PlaceCricketClub
from integrations.rule_engine.rules import PlaceExhibitionConvention
from integrations.rule_engine.rules import PlaceFarm
from integrations.rule_engine.rules import PlaceGolfClub
from integrations.rule_engine.rules import PlaceHotel
from integrations.rule_engine.rules import PlaceLeisureCenterFitnessClub
from integrations.rule_engine.rules import PlaceLibrary
from integrations.rule_engine.rules import PlaceMuseum
from integrations.rule_engine.rules import PlaceO2
from integrations.rule_engine.rules import PlacePark
from integrations.rule_engine.rules import PlaceRacecourse
from integrations.rule_engine.rules import PlaceTheatre
from integrations.rule_engine.rules import PlaceTownHall
from integrations.rule_engine.rules import PlaceUniversityCollege

register = [
    EventPlaceFamily,
    EventPlaceOutdoor,
    # Marks as moderated, do these last.
    PlaceChurchChapelCathedral,
    PlacePark,
    PlaceFarm,
    PlaceExhibitionConvention,
    PlaceConference,
    PlaceHotel,
    PlaceO2,
    PlaceGolfClub,
    PlaceRacecourse,
    PlaceTownHall,
    PlaceCommunityCentre,
    PlaceCricketClub,
    PlaceTheatre,
    PlaceLibrary,
    PlaceUniversityCollege,
    PlaceLeisureCenterFitnessClub,
    PlaceMuseum,
    PlaceArtGallery,
]


class RuleEngine:
    """Rule engine."""

    def __init__(self):
        """Initialise class."""
        self.rules = register

    def apply_rules(self, qs):
        """Apply all the rules to a queryset."""
        for rule in self.rules:
            active = rule()
            active.apply(qs)
