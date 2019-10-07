""" Shared URL patterns.

Add these to your project's `urlpatterns` to avoid duplicating code.
"""
from django.conf.urls import url, include

from auth_backends.views import (
    EdxOAuth2LoginView,
    EdxOAuth2LogoutView,
)

oauth2_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^login/$', EdxOAuth2LoginView.as_view(), name='login'),
    url(r'^logout/$', EdxOAuth2LogoutView.as_view(), name='logout'),
    url('', include('social_django.urls', namespace='social')),
]
