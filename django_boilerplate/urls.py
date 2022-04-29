# -*- coding: utf-8 -*-
"""Root urls."""


# 3rd-party
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.shortcuts import render


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),

    # Basic index view, remove when you want something better.
    path("", lambda request: render(request, "index.html"), name="index"),

]
