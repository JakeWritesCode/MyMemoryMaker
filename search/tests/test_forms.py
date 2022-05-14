# -*- coding: utf-8 -*-
"""Tests for the search forms."""
# Standard Library
from io import BytesIO

# 3rd-party
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from PIL import Image

# Project
from search.forms import NewActivityForm
from search.forms import SearchImageForm
from search.tests.factories import SearchImageFactory
from users.tests.factories import CustomUserFactory


class TestSearchImageForm(TestCase):
    """Tests for the SearchImageForm."""

    def setUp(self) -> None:  # noqa: D102
        self.user = CustomUserFactory()
        self.form = SearchImageForm(user=self.user)

        im = Image.new(mode="RGB", size=(200, 200))  # create a new image using PIL
        self.im_io = BytesIO()  # a BytesIO object for saving image
        im.save(self.im_io, "JPEG")  # save the image to im_io
        self.im_io.seek(0)  # seek to the beginning

        self.image = InMemoryUploadedFile(
            self.im_io,
            None,
            "random-name.jpg",
            "image/jpeg",
            len(self.im_io.getvalue()),
            None,
        )

    def test_layout(self):
        """Test the visual layout properties defined in the form."""
        assert self.form.fields["uploaded_image"].widget.attrs["class"] == "form-control"
        assert (
            self.form.fields["alt_text"].widget.attrs["placeholder"]
            == "Please describe your image."
        )

    def test_form_fields(self):
        """Form should show the correct fields."""
        assert list(self.form.fields.keys()) == [
            "uploaded_image",
            "alt_text",
            "permissions_confirmation",
        ]

    def test_form_adds_uploaded_by_on_save(self):
        """Form should add the attached user to the instance on form save."""
        post_data = {
            "alt_text": "This is an image.",
            "permissions_confirmation": True,
        }
        self.form = SearchImageForm(self.user, data=post_data, files={"uploaded_image": self.image})
        self.form.is_valid()
        instance = self.form.save(commit=True)
        assert instance.uploaded_by == self.user


class TestNewActivityForm(TestCase):
    """Tests for the new activity form."""

    def setUp(self) -> None:  # noqa: D102
        self.user = CustomUserFactory()
        self.form = NewActivityForm(self.user)
        self.fake_post_data = {
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

    def test_form_fails_if_user_is_not_logged_in(self):
        """Form should raise a ValueError if the user is not logged in."""
        with self.assertRaises(ValueError) as e:
            self.form = NewActivityForm(AnonymousUser())
        assert "User must be logged in and passed to this form." in str(e.exception)

    def test_layout(self):
        """Test layout config."""
        assert (
            self.form.fields["headline"].widget.attrs["placeholder"]
            == "Give us a one sentence summary of your activity."
        )
        assert isinstance(self.form.fields["price_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["price_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["duration_upper"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["duration_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["people_lower"].widget, forms.HiddenInput)
        assert isinstance(self.form.fields["people_upper"].widget, forms.HiddenInput)
        assert not self.form.fields["description"].required
        assert (
            self.form.fields["synonyms_keywords"].widget.attrs["placeholder"]
            == "Please seperate words or phrases with commas."
        )

    def test_fields(self):
        """Test that the model shows the correct fields."""
        expected_fields = [
            "headline",
            "description",
            "price_upper",
            "price_lower",
            "duration_upper",
            "duration_lower",
            "people_lower",
            "people_upper",
            "synonyms_keywords",
        ]

        for field in expected_fields:
            assert field in self.form.fields.keys()

    def test_save_raises_attributeerror_if_user_has_not_added_image(self):
        """The associated filters needs to have been added as instance attributes."""
        self.form.image = SearchImageFactory(uploaded_by=self.user)
        with self.assertRaises(AttributeError) as e:
            self.form.save()
        assert "You need to add the filter data and the image." in str(e.exception)

    def test_save_raises_attributeerror_if_user_has_not_added_filters_json(self):
        """The associated image need to have been added as instance attribute."""
        self.form.filters_json = {}
        with self.assertRaises(AttributeError) as e:
            self.form.save()
        assert "You need to add the filter data and the image." in str(e.exception)

    def test_save_adds_created_by_to_instance(self):
        """Save should add created_by to the instance."""
        self.form = NewActivityForm(self.user, data=self.fake_post_data)
        self.form.image = SearchImageFactory(uploaded_by=self.user)
        self.form.filters_json = {}
        instance = self.form.save()
        assert instance.created_by == self.user

    def test_save_adds_filters_to_instance(self):
        """Save should add filters as json to the instance."""
        self.form = NewActivityForm(self.user, data=self.fake_post_data)
        self.form.image = SearchImageFactory(uploaded_by=self.user)
        self.form.filters_json = {"Hey": "There"}
        instance = self.form.save()
        assert instance.attributes == {"Hey": "There"}

    def test_save_adds_image_manytomany_to_instance(self):
        """Save should add image M2M to the instance."""
        self.form = NewActivityForm(self.user, data=self.fake_post_data)
        self.form.image = SearchImageFactory(uploaded_by=self.user)
        self.form.filters_json = {"Hey": "There"}
        instance = self.form.save()
        assert self.form.image in instance.images.all()
