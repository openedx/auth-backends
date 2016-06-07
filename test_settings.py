"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

SECRET_KEY = 'insecure-secret-key'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_nose',
    'auth_backends',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'http://example.com'
SOCIAL_AUTH_EDX_OIDC_KEY = 'dummy-key'
SOCIAL_AUTH_EDX_OIDC_SECRET = 'dummy-secret'
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = 'dummy-secret'

EXTRA_SCOPE = []
COURSE_PERMISSIONS_CLAIMS = []
