# -*- coding: utf-8 -*-
"""Common integration utilities."""
# Standard Library
import time
from http.client import INTERNAL_SERVER_ERROR

# 3rd-party
import requests

# Project
from integrations.exceptions import APIError


def http_request_with_backoff(method, url, retries=5, start_backoff_seconds=1):
    """Perform a HTTP request with backoff. Either returns response or raises an APIError."""
    current_failures = 0
    current_backoff = start_backoff_seconds
    while current_failures < retries:
        method = getattr(requests, method)
        response = method(url)
        if response.status_code == INTERNAL_SERVER_ERROR:
            current_failures += 1
            time.sleep(current_backoff)
            continue
        return response

    raise APIError(
        f"Could not fetch the data correctly from {url} after {current_failures} retries.",
    )
