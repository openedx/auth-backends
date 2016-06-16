""" Shared URL patterns.

Add these to your project's `urlpatterns` to avoid duplicating code.
"""
from django.conf.urls import url, include

from auth_backends.views import EdxOpenIdConnectLoginView, EdxOpenIdConnectLogoutView

auth_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^login/$', EdxOpenIdConnectLoginView.as_view(), name='login'),
    url(r'^logout/$', EdxOpenIdConnectLogoutView.as_view(), name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
