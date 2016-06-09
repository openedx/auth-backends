""" Tests for the views module. """

from django.conf.urls import url
from django.test import TestCase, override_settings

from auth_backends.tests.mixins import LogoutViewTestMixin
from auth_backends.views import LogoutRedirectBaseView

LOGOUT_REDIRECT_URL = 'https://www.example.com/logout/'

urlpatterns = [
    url(r'^logout/$', LogoutRedirectBaseView.as_view(url=LOGOUT_REDIRECT_URL), name='logout'),
]


@override_settings(ROOT_URLCONF=__name__)
class LogoutRedirectBaseViewTests(LogoutViewTestMixin, TestCase):
    """ Tests for LogoutRedirectBaseView. """

    def get_redirect_url(self):
        return LOGOUT_REDIRECT_URL
