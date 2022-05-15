# -*- coding: utf-8 -*-
"""Base settings."""

# Standard Library
from os import getenv
from pathlib import Path

# 3rd-party
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv("DJANGO_SECRET_KEY")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Apps
    "users",
    "search",
    # 3rd party modules
    "crispy_forms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "my_memory_maker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "my_memory_maker.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": getenv("POSTGRES_DB_NAME"),
        "USER": getenv("POSTGRES_DB_USER"),
        "PASSWORD": getenv("POSTGRES_DB_PASSWORD"),
        "HOST": getenv("POSTGRES_DB_HOST"),
        "PORT": getenv("POSTGRES_DB_PORT"),
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = (BASE_DIR / "search/static/", BASE_DIR / "static")
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_ACCESS_KEY_ID = getenv("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = getenv("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "my-memory-maker"
AWS_S3_ENDPOINT_URL = "https://fra1.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
MEDIA_URL = "{}/{}/".format(AWS_S3_ENDPOINT_URL, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CRISPY_TEMPLATE_PACK = "bootstrap4"

AUTH_USER_MODEL = "users.CustomUser"
LOGIN_URL = "/users/log-in"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = getenv("OUTGOING_GMAIL_ADDRESS")
EMAIL_HOST_PASSWORD = getenv("OUTGOING_GMAIL_APP_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST

# Convert django messages to bootstrap.
MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

GOOGLE_MAPS_API_KEY = getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_MAPS_API_SECRET = getenv("GOOGLE_MAPS_API_SECRET")
