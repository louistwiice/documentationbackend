"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from config.conf import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, CORS_ORIGIN_WHITELIST, DATABASE_SQLITE, SWAGGER_BASE_URL, \
    USE_SQLITE, POSTGRES_USER, POSTGRES_DB, POSTGRES_PORT, POSTGRES_PASSWORD, POSTGRES_HOST, ENVIRONMENT

from .base import *

env = environ.Env(DEBUG=(bool, False))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY

ALLOWED_HOSTS = ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS

# CORS: https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST

# Application definition
THIRD_PART_APPS += [
    'corsheaders',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PART_APPS

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if USE_SQLITE is True:
    DATABASES = {
        'default': DATABASE_SQLITE
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': POSTGRES_DB,
            'USER': POSTGRES_USER,
            'PASSWORD': POSTGRES_PASSWORD,
            'HOST': POSTGRES_HOST,
            'PORT': POSTGRES_PORT,
        }
    }

# ===== Sentry settings
SENTRY_DEBUG = env("SENTRY_DEBUG", default=False)

if SENTRY_DEBUG:
    sentry_sdk.init(
        dsn="http://21934a58962e4bb0bba6515f52286b80@10.0.15.60:9000/9",
        integrations=[DjangoIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        environment=ENVIRONMENT,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

# ===== Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
SWAGGER_BASE_URL = SWAGGER_BASE_URL
