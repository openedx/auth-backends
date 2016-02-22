import mock
from django.conf import settings
from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin


class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    backend_path = 'auth_backends.backends.EdXOpenIdConnect'
    url_root = 'http://www.example.com'
    issuer = url_root
    expected_username = 'test_user'
    fake_locale = 'en_US'
    fake_data = {
        'a-claim': 'some-data',
        'another-claim': 'some-other-data'
    }
    fake_access_token = 'an-access-token'

    def extra_settings(self):
        settings = super(EdXOpenIdConnectTests, self).extra_settings()
        settings.update({
            'SOCIAL_AUTH_{0}_URL_ROOT'.format(self.name): self.url_root,
            'SOCIAL_AUTH_{0}_ISSUER'.format(self.name): self.issuer,
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

    @mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json', mock.Mock(return_value=fake_data))
    def test_get_user_claims(self):
        data = self.backend.get_user_claims(self.fake_access_token, claims=['a-claim'])

        self.assertDictEqual(data, {'a-claim': 'some-data'})
