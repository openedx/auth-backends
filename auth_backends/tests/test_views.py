""" Tests for the views module. """

from django.urls import reverse
from django.test import TestCase, override_settings

from auth_backends.tests.mixins import LogoutViewTestMixin
from auth_backends.urls import oauth2_urlpatterns

URL_ROOT = 'https://www.example.com'
LOGOUT_REDIRECT_URL = URL_ROOT + '/logout'

# Django magic to determine which URL patterns are in effect for the tests
urlpatterns = oauth2_urlpatterns


@override_settings(ROOT_URLCONF=__name__)
class EdxOAuth2LoginViewTests(TestCase):
    """ Tests for EdxOAuth2ConnectLoginView. """

    def test_redirect(self):
        """ Verify the view redirects to the edX OAuth2 login page. """
        qs = 'next=/test/'
        response = self.client.get('{url}?{qs}'.format(url=reverse('login'), qs=qs))
        expected = '{url}?{qs}'.format(url=reverse('social:begin', args=['edx-oauth2']), qs=qs)
        self.assertRedirects(response, expected, fetch_redirect_response=False)


@override_settings(ROOT_URLCONF=__name__, URL_ROOT=URL_ROOT)
class EdxOAuth2LogoutView(LogoutViewTestMixin, TestCase):
    """ Tests for EdxOAuth2ConnectLogoutView. """

    def get_redirect_url(self):
        return LOGOUT_REDIRECT_URL
