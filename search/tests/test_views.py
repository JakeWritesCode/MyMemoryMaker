# -*- coding: utf-8 -*-
"""Tests for views.py."""
# Standard Library

# Standard Library
from http.client import OK
from io import BytesIO

# 3rd-party
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

# Project
from search import views
from search.constants import FILTERS
from search.filters import FilterSearchForm
from search.filters import FilterSettingForm
from search.forms import NewActivityForm
from search.forms import SearchImageForm
from search.models import Activity
from search.models import SearchImage
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory
from users.tests.factories import CustomUserFactory
from users.views import log_in


class TestNewActivity(TestCase):
    """Tests for the new_activity view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.new_activity
        self.url = reverse(self.view)
        self.user = CustomUserFactory()

        self.fake_post_data_main_form = {
            "headline": "Test headline",
            "description": "Test description",
            "price_upper": 5,
            "price_lower": 1,
            "duration_upper": 500,
            "duration_lower": 100,
            "people_lower": 2,
            "people_upper": 5,
            "synonyms_keywords": [],
        }

        self.fake_post_data_filters = {}
        for _, filter_list in FILTERS.items():
            for filter_str in filter_list:
                self.fake_post_data_filters[filter_str] = True

        im = Image.new(mode="RGB", size=(200, 200))  # create a new image using PIL
        self.im_io = BytesIO()  # a BytesIO object for saving image
        im.save(self.im_io, "JPEG")  # save the image to im_io
        self.im_io.seek(0)  # seek to the beginning

        self.image = SimpleUploadedFile(
            "random-name.jpg",
            self.im_io.getvalue(),
            "image/jpeg",
        )

        self.fake_post_data_image = {
            "alt_text": "This is an image.",
            "permissions_confirmation": True,
            "uploaded_image": self.image,
        }

    def test_view_requires_login(self):
        """View should require user login."""
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse(log_in) + f"?next={self.url}")

    def test_view_renders_correct_template(self):
        """View should render the correct template."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "partials/new_activity.html")

    def test_context(self):
        """Test that the correct context args are passed."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewActivityForm)
        assert isinstance(response.context["image_form"], SearchImageForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        images = SearchImage.objects.all()
        assert len(images) == 1
        assert images[0].alt_text == "This is an image."

        activities = Activity.objects.all()
        assert len(activities) == 1
        for key, expected in self.fake_post_data_main_form.items():
            assert getattr(activities[0], key) == expected

        for filter_list in FILTERS.values():
            for filter in filter_list:
                assert filter in activities[0].attributes.keys()

    def test_successful_post_request_renders_message(self):
        """A successful post request should return a message to the user."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        assert "Your activity has been saved and has been added" in str(response.content)

    def test_successful_post_request_redirects_to_index(self):
        """A successful post request should redirect to the search home page."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        assert response.wsgi_request.path == reverse("search-home")

    def test_form_does_not_save_if_main_form_is_not_valid(self):
        """If the image form does not validate, nothing should save and errors should be shown."""
        self.fake_post_data_main_form.pop("headline")
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data)
        assert response.status_code == OK
        assert response.context["form"].errors == {"headline": ["This field is required."]}
        assert Activity.objects.count() == 0
        assert SearchImage.objects.count() == 0


class TestSearchView(TestCase):
    """Tests for search_view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.search_view
        self.url = reverse(self.view)

    def test_template(self):
        """Test that the view renders the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "search_home.html")

    def test_context(self):
        """Test that the view renders the correct context."""
        response = self.client.get(self.url)
        assert isinstance(response.context["filter_search_form"], FilterSearchForm)
        assert response.context["GOOGLE_MAPS_API_KEY"] == settings.GOOGLE_MAPS_API_KEY
        assert response.context["filters_dict"] == FILTERS
        assert reverse("search-results") in response.context["search_results_url"]


class TestSearchResults(TestCase):
    """Test search results view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.search_results
        self.url = reverse(self.view)

    def test_template(self):
        """Test that the view returns the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "partials/search_results.html")

    def test_results(self):
        """Functional test to make sure that all results are returned."""
        activity = ActivityFactory()
        event = EventFactory()
        place = PlaceFactory()
        response = self.client.get(self.url)
        assert activity.headline in str(response.content)
        assert event.headline in str(response.content)
        assert place.headline in str(response.content)
