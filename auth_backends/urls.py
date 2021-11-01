""" Shared URL patterns.

Add these to your project's `urlpatterns` to avoid duplicating code.
"""
from django.urls import include, re_path

from auth_backends.views import (
    EdxOAuth2LoginView,
    EdxOAuth2LogoutView,
)

oauth2_urlpatterns = [
    re_path(r'^login/$', EdxOAuth2LoginView.as_view(), name='login'),
    re_path(r'^logout/$', EdxOAuth2LogoutView.as_view(), name='logout'),
    re_path('', include('social_django.urls', namespace='social')),
]
