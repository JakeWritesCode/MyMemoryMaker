# -*- coding: utf-8 -*-
"""Tests for views.py."""
# Standard Library

# Standard Library
import datetime
import uuid
from http.client import CREATED
from http.client import NOT_FOUND
from http.client import OK
from io import BytesIO

# 3rd-party
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

# Project
from search import views
from search.constants import FILTERS
from search.filters import FilterSearchForm
from search.filters import FilterSettingForm
from search.forms import EventDatesForm
from search.forms import NewActivityForm
from search.forms import NewEventForm
from search.forms import NewPlaceForm
from search.forms import SearchImageForm
from search.models import Activity
from search.models import Event
from search.models import Place
from search.models import SearchImage
from search.tests.factories import ActivityFactory
from search.tests.factories import EventFactory
from search.tests.factories import PlaceFactory
from search.tests.factories import SearchImageFactory
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
        assert response.context["partial_target"] == reverse(self.view)

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

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

    def test_successful_post_request_renders_complete_message(self):
        """A successful post request should render the complete message."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        self.assertTemplateUsed(response, "partials/new-activity-complete.html")

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


class TestEditActivity(TestCase):
    """Tests for the edit_activity view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.edit_activity
        self.activity = ActivityFactory()
        self.imageobj = SearchImageFactory()
        self.activity.images.add(self.imageobj)
        self.url = reverse(self.view, args=[self.activity.id])
        self.user = CustomUserFactory(is_staff=True)

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
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, "edit_search_entity.html")

    def test_context(self):
        """Test that the correct context args are passed."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewActivityForm)
        assert isinstance(response.context["image_form"], SearchImageForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)
        assert response.context["entity_type"] == "Activity"
        assert response.context["partial_target"] == self.url
        assert response.context["entity_id"] == str(self.activity.id)

    def test_filters_form_populated_with_correct_filter_info(self):
        """The filter form should be populated with the attributes from the instance."""
        new_filters = {x[0]: True for x in FILTERS.values()}
        unset_filters = [x[1:] for x in FILTERS.values()]
        self.activity.attributes = self.activity.attributes | new_filters
        self.activity.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        for filtername in new_filters.keys():
            assert response.context["filter_setter_form"][filtername].value() is True
        for filter_set in unset_filters:
            for filter_field in filter_set:
                assert response.context["filter_setter_form"][filter_field].value() is None

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

    def test_user_can_save_individual_image_attributes(self):
        """Each validated image attribute should save successfully."""
        self.fake_post_data_image = {"alt_text": "Hey there!"}
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK
        self.imageobj.refresh_from_db()
        assert self.imageobj.alt_text == "Hey there!"

    def test_successful_post_request_renders_complete_message(self):
        """A successful post request should render the complete message."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.assertTemplateUsed(response, "partials/new-activity-complete.html")

    def test_successful_post_marks_activity_as_approved(self):
        """A successful post request should mark the activity as approved."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.activity.refresh_from_db()
        assert self.activity.approved_by == self.user
        self.assertAlmostEquals(
            self.activity.approval_timestamp,
            timezone.now(),
            delta=datetime.timedelta(minutes=1),
        )


class TestNewPlace(TestCase):
    """Tests for the new_place view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.new_place
        self.url = reverse(self.view)
        self.user = CustomUserFactory()
        self.activities = [ActivityFactory(), ActivityFactory()]

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
            "location_lat": 1,
            "location_long": 1.23,
            "activities": [x.id for x in self.activities],
            "google_maps_place_id": "1ac2",
            "place_search": "A place",
            "address": "an address",
            "google_maps_rating": 1.23,
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
        self.assertTemplateUsed(response, "partials/new_place.html")

    def test_context(self):
        """Test that the correct context args are passed."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewPlaceForm)
        assert isinstance(response.context["image_form"], SearchImageForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        images = SearchImage.objects.all()
        assert len(images) == 1
        assert images[0].alt_text == "This is an image."

        places = Place.objects.all()
        assert len(places) == 1
        self.fake_post_data_main_form.pop("place_search")
        self.fake_post_data_main_form.pop("address")
        self.fake_post_data_main_form.pop("activities")
        self.fake_post_data_main_form.pop("google_maps_rating")
        for key, expected in self.fake_post_data_main_form.items():
            assert getattr(places[0], key) == expected

        for filter_list in FILTERS.values():
            for filter in filter_list:
                assert filter in places[0].attributes.keys()

    def test_successful_post_request_renders_complete_message(self):
        """A successful post request should render the complete message."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        self.assertTemplateUsed(response, "partials/new-place-complete.html")

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
        assert Place.objects.count() == 0
        assert SearchImage.objects.count() == 0

    def test_view_saves_data_if_no_uploaded_image_but_link_url(self):
        """If there's a link_url in the POST request, the form should save."""
        self.fake_post_data_image = {"link_url": "Alink"}
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED
        assert Place.objects.count() == 1
        assert Place.objects.first().images.first().display_url == "Alink"

    def test_view_saves_google_maps_data_to_attributes(self):
        """View should add google maps data to the object attributes."""
        self.fake_post_data_image = {"link_url": "Alink"}
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        place = Place.objects.first()
        assert place.attributes["google_maps_data"] == str(
            {"rating": 1.23, "address": "an address"},
        )


class TestEditPlace(TestCase):
    """Tests for the edit place dialog."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.edit_place
        self.activity = ActivityFactory()
        self.place = PlaceFactory()
        self.place.activities.add(self.activity)
        self.image_obj = SearchImageFactory()
        self.place.images.add(self.image_obj)
        self.url = reverse(self.view, args=[self.place.id])
        self.user = CustomUserFactory()
        self.user.is_staff = True
        self.user.save()

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
            "location_lat": 1,
            "location_long": 1.23,
            "activities": [self.activity.id],
            "google_maps_place_id": "1ac2",
            "place_search": "A place",
            "address": "an address",
            "google_maps_rating": 1.23,
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

    def test_view_requires_staff(self):
        """View should require user login."""
        user = CustomUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse("admin:login") + f"?next={self.url}")

        user.is_staff = True
        user.save()
        response = self.client.get(self.url, follow=True)
        assert response.wsgi_request.path_info == self.url

    def test_template_basic_get(self):
        """On a get request, we should get the full edit search entity template."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "edit_search_entity.html")

    def test_form_populated_with_instance_info(self):
        """The main form should have the instance assigned."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.context["form"].instance == self.place

    def test_image_form_has_instance_and_configured(self):
        """The image form should be configured."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.context["image_form"].instance == self.image_obj
        assert response.context["image_form"].fields["permissions_confirmation"].required is False

    def test_image_form_populated_with_new_image_if_one_does_not_exist(self):
        """If there is no image attached, generate a new one."""
        self.image_obj.delete()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["image_form"].instance, SearchImage)
        assert SearchImage.objects.filter(id=response.context["image_form"].instance.id).count() == 0
        assert response.context["image_form"].fields["permissions_confirmation"].required is False


    def test_filters_form_populated_with_correct_filter_info(self):
        """The filter form should be populated with the attributes from the instance."""
        new_filters = {x[0]: True for x in FILTERS.values()}
        unset_filters = [x[1:] for x in FILTERS.values()]
        self.place.attributes = self.place.attributes | new_filters
        self.place.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        for filtername in new_filters.keys():
            assert response.context["filter_setter_form"][filtername].value() is True
        for filter_set in unset_filters:
            for filter_field in filter_set:
                assert response.context["filter_setter_form"][filter_field].value() is None

    def test_template_post(self):
        """On a POST request, we should jsut return the form partial."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "partials/new_place.html")

    def test_image_form_permissions_required_not_required_if_link_url(self):
        """If there's a link_url, don't require the upload permission checkbox."""
        self.client.force_login(self.user)
        post_data = {"link_url": "Abc123"}
        response = self.client.post(self.url, data=post_data)
        assert response.context["image_form"].fields["permissions_confirmation"].required is False

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.image_obj.refresh_from_db()
        assert self.image_obj.alt_text == "This is an image."

        places = Place.objects.all()
        assert len(places) == 1
        self.fake_post_data_main_form.pop("place_search")
        self.fake_post_data_main_form.pop("address")
        self.fake_post_data_main_form.pop("activities")
        self.fake_post_data_main_form.pop("google_maps_rating")
        for key, expected in self.fake_post_data_main_form.items():
            assert getattr(places[0], key) == expected

        for filter_list in FILTERS.values():
            for filter in filter_list:
                assert filter in places[0].attributes.keys()

    def test_image_form_saves_each_attribute_separately(self):
        """The image form should save each changed attr separately."""
        self.fake_post_data_image = {"alt_text": "Wazzap!", "uploaded_image": ""}
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.image_obj.refresh_from_db()
        assert self.image_obj.alt_text == "Wazzap!"

    def test_save_saves_google_maps_data_in_attributes(self):
        """Save should save the correct google maps data in attributes."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.place.refresh_from_db()
        assert self.place.attributes["google_maps_data"] == str(
            {
                "rating": 1.23,
                "address": "an address",
            },
        )

    def test_save_renders_correct_template(self):
        """Save should render the correct template."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.assertTemplateUsed(response, "partials/new-place-complete.html")

    def test_context(self):
        """Test context."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewPlaceForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)
        assert response.context["entity_type"] == "Place"
        assert response.context["partial_target"] == reverse(views.edit_place, args=[self.place.id])
        assert response.context["GOOGLE_MAPS_API_KEY"] == settings.GOOGLE_MAPS_API_KEY
        assert response.context["entity_id"] == str(self.place.id)

    def test_successful_post_marks_place_as_approved(self):
        """A successful post request should mark the place as approved."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.place.refresh_from_db()
        assert self.place.approved_by == self.user
        self.assertAlmostEquals(
            self.place.approval_timestamp,
            timezone.now(),
            delta=datetime.timedelta(minutes=1),
        )


class TestNewEvent(TestCase):
    """Tests for the new_event view."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.new_event
        self.url = reverse(self.view)
        self.user = CustomUserFactory()
        self.activities = [ActivityFactory(), ActivityFactory()]
        self.places = [PlaceFactory(), PlaceFactory()]
        self.dates = [
            datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
            datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        ]

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
            "activities": [x.id for x in self.activities],
            "places": [x.id for x in self.places],
            "from_date": datetime.datetime.strftime(self.dates[0], "%d/%m/%Y, %H:%M"),
            "to_date": datetime.datetime.strftime(self.dates[1], "%d/%m/%Y, %H:%M"),
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
        self.assertTemplateUsed(response, "partials/new_event.html")

    def test_context(self):
        """Test that the correct context args are passed."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewEventForm)
        assert isinstance(response.context["image_form"], SearchImageForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        images = SearchImage.objects.all()
        assert len(images) == 1
        assert images[0].alt_text == "This is an image."

        events = Event.objects.all()
        self.fake_post_data_main_form.pop("from_date")
        self.fake_post_data_main_form.pop("to_date")
        self.fake_post_data_main_form.pop("activities")
        self.fake_post_data_main_form.pop("places")
        assert len(events) == 1
        for key, expected in self.fake_post_data_main_form.items():
            assert getattr(events[0], key) == expected

        assert events[0].dates == [self.dates]
        assert list(events[0].activities.all()) == self.activities
        assert list(events[0].places.all()) == self.places

        for filter_list in FILTERS.values():
            for filter in filter_list:
                assert filter in events[0].attributes.keys()

    def test_successful_post_request_renders_complete_message(self):
        """A successful post request should render the complete message."""
        post_data = (
            self.fake_post_data_filters | self.fake_post_data_main_form | self.fake_post_data_image
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == CREATED

        self.assertTemplateUsed(response, "partials/new-event-complete.html")

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
        assert Event.objects.count() == 0
        assert SearchImage.objects.count() == 0


class TestEditEvent(TestCase):
    """Tests for the edit event dialog."""

    def setUp(self) -> None:  # noqa: D102
        self.view = views.edit_event
        self.activity = ActivityFactory()
        self.place = PlaceFactory()
        self.event = EventFactory()
        self.event.activities.add(self.activity)
        self.event.places.add(self.place)
        self.image_obj = SearchImageFactory()
        self.event.images.add(self.image_obj)
        self.url = reverse(self.view, args=[self.event.id])
        self.user = CustomUserFactory()
        self.user.is_staff = True
        self.user.save()

        self.dates = [
            datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
            datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        ]

        self.fake_post_data_dates_form = {
            "from_date": "01/01/2022, 00:00",
            "to_date": "01/01/2023, 00:00",
        }

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
            "activities": [self.activity.id],
            "places": [self.place.id],
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

    def test_view_requires_staff(self):
        """View should require user login."""
        user = CustomUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse("admin:login") + f"?next={self.url}")

        user.is_staff = True
        user.save()
        response = self.client.get(self.url, follow=True)
        assert response.wsgi_request.path_info == self.url

    def test_template_basic_get(self):
        """On a get request, we should get the full edit search entity template."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "edit_search_entity.html")

    def test_form_populated_with_instance_info(self):
        """The main form should have the instance assigned."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.context["form"].instance == self.event

    def test_image_form_has_instance_and_configured(self):
        """The image form should be configured."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.context["image_form"].instance == self.image_obj
        assert response.context["image_form"].fields["permissions_confirmation"].required is False

    def test_filters_form_populated_with_correct_filter_info(self):
        """The filter form should be populated with the attributes from the instance."""
        new_filters = {x[0]: True for x in FILTERS.values()}
        unset_filters = [x[1:] for x in FILTERS.values()]
        self.event.attributes = self.event.attributes | new_filters
        self.event.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        for filtername in new_filters.keys():
            assert response.context["filter_setter_form"][filtername].value() is True
        for filter_set in unset_filters:
            for filter_field in filter_set:
                assert response.context["filter_setter_form"][filter_field].value() is None

    def test_template_post(self):
        """On a POST request, we should jsut return the form partial."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "partials/new_event.html")

    def test_image_form_permissions_required_not_required(self):
        """Permissions should be not required."""
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={})
        assert response.context["image_form"].fields["permissions_confirmation"].required is False

    def test_successful_post_request_saves_form(self):
        """A successful post request should save all data."""
        post_data = (
            self.fake_post_data_filters
            | self.fake_post_data_main_form
            | self.fake_post_data_image
            | self.fake_post_data_dates_form
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.image_obj.refresh_from_db()
        assert self.image_obj.alt_text == "This is an image."

        events = Event.objects.all()
        assert len(events) == 1
        self.fake_post_data_main_form.pop("activities")
        self.fake_post_data_main_form.pop("places")
        for key, expected in self.fake_post_data_main_form.items():
            assert getattr(events[0], key) == expected

        assert list(events[0].activities.all()) == [self.activity]
        assert list(events[0].places.all()) == [self.place]

        for filter_list in FILTERS.values():
            for filter in filter_list:
                assert filter in events[0].attributes.keys()

        assert events[0].dates == [self.dates]

    def test_image_form_saves_each_attribute_separately(self):
        """The image form should save each changed attr separately."""
        self.fake_post_data_image = {"alt_text": "Wazzap!"}
        post_data = (
            self.fake_post_data_filters
            | self.fake_post_data_main_form
            | self.fake_post_data_image
            | self.fake_post_data_dates_form
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.image_obj.refresh_from_db()
        assert self.image_obj.alt_text == "Wazzap!"

    def test_save_renders_correct_template(self):
        """Save should render the correct template."""
        post_data = (
            self.fake_post_data_filters
            | self.fake_post_data_main_form
            | self.fake_post_data_image
            | self.fake_post_data_dates_form
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.assertTemplateUsed(response, "partials/new-event-complete.html")

    def test_context(self):
        """Test context."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert isinstance(response.context["form"], NewEventForm)
        assert isinstance(response.context["filter_setter_form"], FilterSettingForm)
        assert isinstance(response.context["event_dates_form"], EventDatesForm)
        assert response.context["entity_type"] == "Event"
        assert response.context["partial_target"] == reverse(views.edit_event, args=[self.event.id])
        assert response.context["GOOGLE_MAPS_API_KEY"] == settings.GOOGLE_MAPS_API_KEY
        assert response.context["entity_id"] == str(self.event.id)

    def test_successful_post_marks_event_as_approved(self):
        """A successful post request should mark the event as approved."""
        post_data = (
            self.fake_post_data_filters
            | self.fake_post_data_main_form
            | self.fake_post_data_image
            | self.fake_post_data_dates_form
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=post_data, follow=True)
        assert response.status_code == OK

        self.event.refresh_from_db()
        assert self.event.approved_by == self.user
        self.assertAlmostEquals(
            self.event.approval_timestamp,
            timezone.now(),
            delta=datetime.timedelta(minutes=1),
        )


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
        user = CustomUserFactory()
        activity = ActivityFactory(approved_by=user, approval_timestamp=timezone.now())
        event = EventFactory(approved_by=user, approval_timestamp=timezone.now())
        place = PlaceFactory(approved_by=user, approval_timestamp=timezone.now())
        response = self.client.get(self.url)
        assert activity.headline in str(response.content)
        assert event.headline in str(response.content)
        assert place.headline in str(response.content)


class TestNewEntityWizard(TestCase):
    """Test new entity wizard."""

    def setUp(self) -> None:  # noqa: D102
        self.user = CustomUserFactory()
        self.client.force_login(self.user)
        self.view = views.new_entity_wizard
        self.url = reverse(self.view)

    def test_template(self):
        """Test that the view returns the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "new_entity_wizard.html")

    def test_context(self):
        """Test that the view renders the correct context."""
        response = self.client.get(self.url)
        assert response.context["GOOGLE_MAPS_API_KEY"] == settings.GOOGLE_MAPS_API_KEY


class TestSeeMore(TestCase):
    """Tests for the see more view."""

    def setUp(self) -> None:  # noqa: D102
        self.event = EventFactory()
        self.place = PlaceFactory()
        self.event.places.add(self.place)
        self.view = views.see_more
        self.url = reverse(self.view, args=["Event", self.event.id])

    def test_view_returns_error_message_if_entity_type_is_not_correct(self):
        """If the entity type is incorrect return a 404."""
        response = self.client.get(reverse(self.view, args=["Not", "a123"]))
        assert response.status_code == NOT_FOUND
        assert "The entity type you requested does not exist." in str(response.content)

    def test_view_returns_error_message_if_entity_id_is_not_correct(self):
        """If the entity id is incorrect return a 404."""
        response = self.client.get(reverse(self.view, args=["Event", uuid.uuid4()]))
        assert response.status_code == NOT_FOUND
        assert "The entity ID you requested does not exist." in str(response.content)

    def test_template(self):
        """Test that the view returns the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "see_more.html")

    def test_context(self):
        """Test that the view renders the correct context."""
        response = self.client.get(self.url)
        assert response.context["search_entity"] == self.event
        assert response.context["entity_type"] == "Event"
