from pathlib import Path

from .config import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.secret_key
DEBUG = config.debug

ALLOWED_HOSTS = list(config.allowed_hosts)
if DEBUG:
    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "0.0.0.0"])

INSTALLED_APPS = [
    "apps.reviewer",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smart_code_reviewer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "smart_code_reviewer.wsgi.application"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

OPENAI_API_KEY = config.openai_api_key
OPENAI_MODEL = config.openai_model
