# -*- coding: utf-8 -*-
"""Views for integrations. Most of these will just be ways to manually call tasks."""
# 3rd-party
import json

import requests
from django.http import HttpResponse

# Project
from integrations.eventbrite import EventBriteEventParser
from integrations.eventbrite import EventIDDownloader
from integrations.eventbrite import EventRawDataDownloader


def get_eventbrite_event_ids(request):
    """Manually start the Eventbrite event ID download process."""
    downloader = EventIDDownloader()
    downloader.get_event_ids()
    return HttpResponse("Complete", status=200)


def get_eventbrite_raw_event_data(request):
    """Manually start the Eventbrite event data download process."""
    downloader = EventRawDataDownloader()
    downloader.get_recently_seen_events()
    return HttpResponse("Complete", status=200)


def parse_eventbrite_data_into_events(request):
    """Manually start the Eventbrite event parsing process."""
    downloader = EventBriteEventParser()
    downloader.process_data()
    return HttpResponse("Complete", status=200)

def parse_categories(request):
    category_mapping = {}
    response = requests.get("https://www.eventbriteapi.com/v3/categories/?token=4HA7TMIXBZANQUNK62EE")
    json_response = json.loads(response.content)
    for cat in json_response["categories"]:
        category_mapping[cat["name"]] = {
            "id": cat["id"],
            "subcategories": []
        }
    for i in range(1, 6):
        response = requests.get(
            f"https://www.eventbriteapi.com/v3/subcategories/?token=4HA7TMIXBZANQUNK62EE&page={i}")
        json_response = json.loads(response.content)
        try:
            for subcat in json_response["subcategories"]:
                category_mapping[subcat["parent_category"]["name"]]["subcategories"].append(
                    {"id": subcat["id"], "name": subcat["name"]}
                )
        except KeyError:
            hello  =1
    hello = 1