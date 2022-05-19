# -*- coding: utf-8 -*-
"""Root urls."""


# 3rd-party
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include
from django.urls import path
from django.urls import reverse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("search/", include("search.urls")),
    # Basic index view, remove when you want something better.
    path("", lambda request: redirect(reverse("search-home")), name="index"),
]
