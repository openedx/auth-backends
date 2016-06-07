""" Test mixins. """

from django.contrib.auth import get_user, get_user_model
from django.core.urlresolvers import reverse

User = get_user_model()


class LogoutViewTestMixin(object):
    """ Mixin for tests of the LogoutRedirectBaseView children. """

    def get_logout_url(self):
        """ Returns the URL of the logout view. """
        return reverse('logout')

    def get_redirect_url(self):
        """ Returns the URL to which the user should be redirected after logout. """
        raise NotImplementedError  # pragma: no cover

    def assert_authentication_status(self, is_authenticated):
        """ Verifies the authentication status of the user attached to the test client. """
        user = get_user(self.client)
        self.assertEqual(user.is_authenticated(), is_authenticated)

    def test_redirect_url(self):
        """ Verify the view redirects to the correct URL. """
        response = self.client.get(self.get_logout_url())
        self.assertRedirects(response, self.get_redirect_url(), fetch_redirect_response=False)

    def test_x_frame_options_header(self):
        """ Verify no X-Frame-Options header is set in the resposne. """
        response = self.client.get(self.get_logout_url())
        self.assertNotIn('X-Frame-Options', response)

    def test_logout(self):
        """ Verify the user is logged out of the current session. """
        self.client.logout()
        self.assert_authentication_status(False)

        password = 'test'
        user = User.objects.create_user('test', password=password)
        self.client.login(username=user.username, password=password)
        self.assert_authentication_status(True)

        self.client.get(self.get_logout_url())
        self.assert_authentication_status(False)

    def test_no_redirect(self):
        """ Verify the view does not redirect if the no_redirect querystring parameter is set. """
        response = self.client.get(self.get_logout_url(), {'no_redirect': 1})
        self.assertEqual(response.status_code, 200)
