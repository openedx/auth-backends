""" Shared URL patterns.

Add these to your project's `urlpatterns` to avoid duplicating code.
"""
from django.urls import path
from django.urls import include

from auth_backends.views import (
    EdxOAuth2LoginView,
    EdxOAuth2LogoutView,
)

oauth2_urlpatterns = [
    path('login/', EdxOAuth2LoginView.as_view(), name='login'),
    path('logout/', EdxOAuth2LogoutView.as_view(), name='logout'),
    path('', include('social_django.urls', namespace='social')),
]
