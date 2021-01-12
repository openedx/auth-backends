""" Tests for the backends. """
import datetime
import json
from calendar import timegm

import six
from Cryptodome.PublicKey import RSA
from django.core.cache import cache
from jwkest.jwk import RSAKey
from jwkest.jws import JWS
from social_core.tests.backends.oauth import OAuth2Test


class EdXOAuth2Tests(OAuth2Test):
    """ Tests for the EdXOAuth2 backend. """

    backend_path = 'auth_backends.backends.EdXOAuth2'
    client_key = 'a-key'
    client_secret = 'a-secret-key'
    expected_username = 'jsmith'
    url_root = 'https://example.com'
    public_url_root = 'https://public.example.com'
    logout_redirect_url = 'https://example.com/logout_redirect'

    def setUp(self):
        cache.clear()
        super().setUp()
        self.key = RSAKey(kid='testkey', key=RSA.generate(2048))

    def set_social_auth_setting(self, setting_name, value):
        """
        Set a social auth django setting during the middle of a test.
        """
        # The inherited backend defines self.name, i.e. "EDX_OAUTH2".
        backend_name = self.name

        # NOTE: We use the strategy's method, rather than override_settings, because the TestStrategy class being used
        # does not rely on Django settings.
        self.strategy.set_settings({f'SOCIAL_AUTH_{backend_name}_{setting_name}': value})

    def access_token_body(self, request, _url, headers):
        """ Generates a response from the provider's access token endpoint. """
        # The backend should always request JWT access tokens, not Bearer.
        body = six.moves.urllib.parse.parse_qs(request.body.decode('utf8'))
        self.assertEqual(body['token_type'], ['jwt'])

        expires_in = 3600
        access_token = self.create_jws_access_token(expires_in)
        body = json.dumps({
            'scope': 'read write profile email user_id',
            'token_type': 'JWT',
            'expires_in': expires_in,
            'access_token': access_token
        })
        return 200, headers, body

    def create_jws_access_token(self, expires_in=3600, issuer=None, key=None, alg='RS512'):
        """
        Creates a signed (JWS) access token.

        Arguments:
            expires_in (int): Number of seconds after which the token expires.
            issuer (str): Issuer of the token.
            key (jwkest.jwk.Key): Key used to sign the token.
            alg (str): Signing algorithm.

        Returns:
            str: JWS
        """
        key = key or self.key
        now = datetime.datetime.utcnow()
        expiration_datetime = now + datetime.timedelta(seconds=expires_in)
        issue_datetime = now
        payload = {
            'iss': issuer or self.url_root,
            'administrator': False,
            'iat': timegm(issue_datetime.utctimetuple()),
            'given_name': 'Joe',
            'sub': 'e3bfe0e4e7c6693efba9c3a93ee7f31b',
            'preferred_username': self.expected_username,
            'aud': 'InkocujLikyucsEdwiWatdebrEackmevLakDuifKooshkakWow',
            'scopes': ['read', 'write', 'profile', 'email', 'user_id'],
            'email': 'jsmith@example.com',
            'exp': timegm(expiration_datetime.utctimetuple()),
            'name': 'Joe Smith',
            'family_name': 'Smith',
            'user_id': '1',
        }
        access_token = JWS(payload, jwk=key, alg=alg).sign_compact()
        return access_token

    def extra_settings(self):
        """
        Create extra Django settings for use with tests.
        """
        settings = super().extra_settings()
        settings.update({
            f'SOCIAL_AUTH_{self.name}_KEY': self.client_key,
            f'SOCIAL_AUTH_{self.name}_SECRET': self.client_secret,
            f'SOCIAL_AUTH_{self.name}_URL_ROOT': self.url_root,
        })
        return settings

    def test_login(self):
        self.do_login()

    def test_partial_pipeline(self):
        self.do_partial_pipeline()

    def test_logout_url(self):
        """
        Verify the property returns the provider's logout URL.
        """
        logout_url_without_query_params = f'{self.url_root}/logout'

        self.assertEqual(
            self.backend.logout_url,
            logout_url_without_query_params,
        )

        self.set_social_auth_setting('LOGOUT_REDIRECT_URL', self.logout_redirect_url)

        expected_query_params = f'?client_id={self.client_key}&redirect_url={self.logout_redirect_url}'

        self.assertEqual(
            self.backend.logout_url,
            logout_url_without_query_params + expected_query_params,
        )

    def test_authorization_url(self):
        """
        Verify the method utilizes the public URL, if one is set.
        """
        authorize_location = '/oauth2/authorize'
        self.assertEqual(self.backend.authorization_url(), self.url_root + authorize_location)

        # Now, add the public url root to the settings.
        self.set_social_auth_setting('PUBLIC_URL_ROOT', self.public_url_root)
        self.assertEqual(self.backend.authorization_url(), self.public_url_root + authorize_location)

    def test_end_session_url(self):
        """
        Verify the method returns the provider's logout URL (sans any redirect URLs in the query parameters).
        """
        logout_location = '/logout'
        self.assertEqual(self.backend.end_session_url(), self.url_root + logout_location)

        # Now, add the public url root to the settings.
        self.set_social_auth_setting('PUBLIC_URL_ROOT', self.public_url_root)
        self.assertEqual(self.backend.end_session_url(), self.public_url_root + logout_location)

    def test_user_data(self):
        user_data = self.backend.user_data(self.create_jws_access_token())
        self.assertDictEqual(user_data, {
            'name': 'Joe Smith',
            'preferred_username': 'jsmith',
            'email': 'jsmith@example.com',
            'given_name': 'Joe',
            'user_id': '1',
            'family_name': 'Smith',
            'administrator': False
        })

    def test_extra_data(self):
        """
        Ensure that `user_id` and `refresh_token` stay in EXTRA_DATA.
        The refresh token is required to refresh the user's access
        token in cases where the client_credentials grant type is not
        being used, and the application is running on a completely
        separate domain name.
        """
        self.assertEqual(self.backend.EXTRA_DATA, [
            ('user_id', 'user_id', True),
            ('refresh_token', 'refresh_token', True),
        ])
