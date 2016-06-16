""" Tests for the views module. """

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from auth_backends.tests.mixins import LogoutViewTestMixin
from auth_backends.urls import auth_urlpatterns

LOGOUT_REDIRECT_URL = 'https://www.example.com/logout/'

urlpatterns = auth_urlpatterns


@override_settings(ROOT_URLCONF=__name__)
class EdxOpenIdConnectLoginViewTests(TestCase):
    """ Tests for EdxOpenIdConnectLoginView. """

    def test_redirect(self):
        """ Verify the view redirects to the edX OIDC login page. """
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('social:begin', args=['edx-oidc']), fetch_redirect_response=False)


@override_settings(ROOT_URLCONF=__name__, SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL=LOGOUT_REDIRECT_URL)
class EdxOpenIdConnectLogoutView(LogoutViewTestMixin, TestCase):
    """ Tests for EdxOpenIdConnectLogoutView. """

    def get_redirect_url(self):
        return LOGOUT_REDIRECT_URL
