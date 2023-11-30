INSTALLED_APPS = [
'django.contrib.sessions',
]
MIDDLEWARE = [
'django.contrib.session.middleware.SessionMiddleware',
]
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'