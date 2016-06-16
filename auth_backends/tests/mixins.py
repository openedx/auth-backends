""" Test mixins. """

from django.contrib.auth import get_user, get_user_model
from django.core.urlresolvers import reverse
from social.apps.django_app.default.models import UserSocialAuth

PASSWORD = 'test'
User = get_user_model()


class LogoutViewTestMixin(object):
    """ Mixin for tests of the LogoutRedirectBaseView children. """

    def create_user(self):
        """ Create a new user. """
        user = User.objects.create_user('test', password=PASSWORD)
        UserSocialAuth.objects.create(user=user, provider='edx-oidc', uid=user.username)
        return user

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

    def test_x_frame_options_header(self):
        """ Verify no X-Frame-Options header is set in the resposne. """
        response = self.client.get(self.get_logout_url())
        self.assertNotIn('X-Frame-Options', response)

    def test_logout(self):
        """ Verify the user is logged out of the current session and redirected to the appropriate URL. """
        self.client.logout()
        self.assert_authentication_status(False)

        user = self.create_user()
        self.client.login(username=user.username, password=PASSWORD)
        self.assert_authentication_status(True)

        response = self.client.get(self.get_logout_url())
        self.assert_authentication_status(False)
        self.assertRedirects(response, self.get_redirect_url(), fetch_redirect_response=False)

    def test_no_redirect(self):
        """ Verify the view does not redirect if the no_redirect querystring parameter is set. """
        response = self.client.get(self.get_logout_url(), {'no_redirect': 1})
        self.assertEqual(response.status_code, 200)
