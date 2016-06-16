""" Tests for the backends. """

import ddt
import mock
import six
from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin


@ddt.ddt
class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    """ Tests for the EdXOpenIdConnect backend. """

    backend_path = 'auth_backends.backends.EdXOpenIdConnect'
    url_root = 'http://www.example.com'
    logout_url = 'http://www.example.com/logout/'
    issuer = url_root
    expected_username = 'test_user'
    fake_locale = 'en_US'
    fake_data = {
        'a-claim': 'some-data',
        'another-claim': 'some-other-data'
    }
    fake_access_token = 'an-access-token'

    def extra_settings(self):
        """ Define additional Django settings. """
        settings = super(EdXOpenIdConnectTests, self).extra_settings()
        settings.update({
            'SOCIAL_AUTH_{0}_URL_ROOT'.format(self.name): self.url_root,
            'SOCIAL_AUTH_{0}_ISSUER'.format(self.name): self.issuer,
            'SOCIAL_AUTH_{0}_LOGOUT_URL'.format(self.name): self.logout_url,
        })
        return settings

    def get_id_token(self, *args, **kwargs):
        data = super(EdXOpenIdConnectTests, self).get_id_token(*args, **kwargs)

        # Set the field used to derive the username of the logged user.
        data['preferred_username'] = self.expected_username

        # Exercise the locale name to language code path
        data['locale'] = self.fake_locale

        return data

    def test_login(self):
        user = self.do_login()
        self.assertIsNotNone(user)

    @ddt.data(None, 'Bearer', 'JWT')
    def test_get_user_claims(self, token_type):
        expected_token_type = token_type or 'Bearer'
        with mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json') as mock_get_json:
            mock_get_json.return_value = self.fake_data

            claim = six.next(six.iteritems(self.fake_data))
            kwargs = {
                'claims': [claim[0]],
            }

            if token_type:
                kwargs['token_type'] = token_type

            actual = self.backend.get_user_claims(self.fake_access_token, **kwargs)

            # Verify the correct claim data is returned
            self.assertDictEqual(actual, {claim[0]: claim[1]})

            # Verify the call to the user info endpoint was made with the correct authorization headers
            headers = {'Authorization': '{token_type} {token}'.format(token_type=expected_token_type,
                                                                      token=self.fake_access_token)}
            mock_get_json.assert_called_once_with(self.backend.USER_INFO_URL, headers=headers)

    def test_logout_url(self):
        """ Verify the property returns the configured logout URL. """
        self.assertEqual(self.backend.logout_url, self.logout_url)
