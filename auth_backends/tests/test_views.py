""" Tests for the views module. """

from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from auth_backends.tests.mixins import LogoutViewTestMixin
from auth_backends.urls import auth_urlpatterns
from auth_backends.views import LogoutRedirectBaseView

LOGOUT_REDIRECT_URL = 'https://www.example.com/logout/'

urlpatterns = auth_urlpatterns + [
    url(r'^logout/$', LogoutRedirectBaseView.as_view(url=LOGOUT_REDIRECT_URL), name='logout'),
]


@override_settings(ROOT_URLCONF=__name__)
class LogoutRedirectBaseViewTests(LogoutViewTestMixin, TestCase):
    """ Tests for LogoutRedirectBaseView. """

    def get_redirect_url(self):
        return LOGOUT_REDIRECT_URL


@override_settings(ROOT_URLCONF=__name__)
class EdxOpenIdConnectLoginViewTests(TestCase):
    """ Tests for EdxOpenIdConnectLoginView. """

    def test_redirect(self):
        """ Verify the view redirects to the edX OIDC login page. """
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('social:begin', args=['edx-oidc']), fetch_redirect_response=False)
