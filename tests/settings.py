"""Django settings used when testing."""


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('admin', 'admin@example.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## IN-MEMORY TEST DATABASE
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = ''

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = ''
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
STATIC_ROOT = ''

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
STATIC_URL = '/static/'
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for testing.
SECRET_KEY = 'insecure-secret-key'
########## END SECRET CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## APP CONFIGURATION
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'auth_backends',
)
########## END APP CONFIGURATION


########## TEST SETTINGS
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'http://example.com'
SOCIAL_AUTH_EDX_OIDC_KEY = 'dummy-key'
SOCIAL_AUTH_EDX_OIDC_SECRET = 'dummy-secret'
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = 'dummy-secret'

EXTRA_SCOPE = []
COURSE_PERMISSIONS_CLAIMS = []

INSTALLED_APPS += (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
########## END TEST SETTINGS
