""" Tests for the views module. """

from django.conf.urls import url
from django.contrib.auth import get_user_model, get_user
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from auth_backends.views import LogoutRedirectBaseView

LOGOUT_REDIRECT_URL = 'https://www.example.com/logout/'
User = get_user_model()

urlpatterns = [
    url(r'^logout/$', LogoutRedirectBaseView.as_view(url=LOGOUT_REDIRECT_URL), name='logout'),
]


@override_settings(ROOT_URLCONF=__name__)
class LogoutRedirectBaseViewTests(TestCase):
    """ Tests for LogoutRedirectBaseView. """

    def assert_authentication_status(self, is_authenticated):
        """ Verifies the authentication status of the user attached to the test client. """
        user = get_user(self.client)
        self.assertEqual(user.is_authenticated(), is_authenticated)

    def test_redirect_url(self):
        """ Verify the view redirects to the correct URL. """
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, LOGOUT_REDIRECT_URL, fetch_redirect_response=False)

    def test_x_frame_options_header(self):
        """ Verify no X-Frame-Options header is set in the resposne. """
        response = self.client.get(reverse('logout'))
        self.assertNotIn('X-Frame-Options', response)

    def test_logout(self):
        """ Verify the user is logged out of the current session. """
        self.client.logout()
        self.assert_authentication_status(False)

        password = 'test'
        user = User.objects.create_user('test', password=password)
        self.client.login(username=user.username, password=password)
        self.assert_authentication_status(True)

        self.client.get(reverse('logout'))
        self.assert_authentication_status(False)

    def test_no_redirect(self):
        """ Verify the view does not redirect if the no_redirect querystring parameter is set. """
        response = self.client.get(reverse('logout') + '?no_redirect=1')
        self.assertEqual(response.status_code, 200)
