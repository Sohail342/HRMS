from .base import *


DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOW_HOSTS", "").split(",")

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware', 
]



# Base settings for production
DATABASES = {
    'default': {
        'ENGINE': os.getenv("PRO_DATABASE_ENGINE"),
        'NAME': os.getenv("PRO_DATABASE_NAME"),
        'USER': os.getenv("PRO_DATABASE_USER"),
        'PASSWORD': os.getenv("PRO_DATABASE_PASSWORD"),
        'HOST': os.getenv("PRO_DATABASE_HOST"),
        'PORT': os.getenv("PRO_DATABASE_PORT"),
    }
}