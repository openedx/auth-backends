""" Tests for the backends. """
import datetime
import json
import unittest
from calendar import timegm

import ddt
import mock
import pytest
import six
from Cryptodome.PublicKey import RSA
from django.core.cache import cache
from httpretty import HTTPretty
from jwkest.jwk import SYMKey, RSAKey, KEYS
from jwkest.jws import JWS
from jwkest.jwt import b64encode_item
from social_core.exceptions import AuthTokenError
from social_core.tests.backends.oauth import OAuth2Test
from social_core.tests.backends.open_id_connect import OpenIdConnectTestMixin

from auth_backends.backends import EdXOpenIdConnect
from auth_backends.strategies import EdxDjangoStrategy


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

    # NOTE (CCB): We don't use this, but it's required by OpenIdConnectTestMixin.setUp().
    openid_config_body = '{ "jwks_uri": "http://www.example.com" }'

    def setUp(self):
        super(EdXOpenIdConnectTests, self).setUp()
        self.key = SYMKey(key=self.client_secret)

    # NOTE (CCB): We are TEMPORARILY disabling the nonce validation while we transition our
    # authentication provider to properly implement storing the nonce at the point of initial
    # authorization, rather than when we request the access token.
    def access_token_body(self, request, _url, headers):  # pylint: disable=method-hidden
        """
        Get the nonce from the request parameters, add it to the id_token, and
        return the complete response.
        """
        # nonce = self.backend.data['nonce'].encode('utf-8')
        # body = self.prepare_access_token_body(nonce=nonce)
        body = self.prepare_access_token_body()
        return 200, headers, body

    @unittest.skip('Disabled until we release https://github.com/edx/edx-platform/pull/14966.')
    def test_invalid_nonce(self):
        self.authtoken_raised(
            'Token error: Incorrect id_token: nonce',
            nonce='something-wrong'
        )

    def extra_settings(self):
        """ Define additional Django settings. """
        settings = super(EdXOpenIdConnectTests, self).extra_settings()
        settings.update({
            'SOCIAL_AUTH_{0}_URL_ROOT'.format(self.name): self.url_root,
            'SOCIAL_AUTH_{0}_ISSUER'.format(self.name): self.issuer,
            'SOCIAL_AUTH_{0}_LOGOUT_URL'.format(self.name): self.logout_url,
        })

        # Use settings from our default strategy so that we can validate them
        settings.update(EdxDjangoStrategy.DEFAULT_SETTINGS)

        return settings

    def get_id_token(self, client_key=None, expiration_datetime=None, issue_datetime=None, nonce=None, issuer=None):
        data = super(EdXOpenIdConnectTests, self).get_id_token(
            client_key, expiration_datetime, issue_datetime, nonce, issuer)

        # Set the field used to derive the username of the logged user.
        data['preferred_username'] = self.expected_username

        # Exercise the locale name to language code path
        data['locale'] = self.fake_locale

        return data

    def prepare_access_token_body(self, client_key=None, tamper_message=False, expiration_datetime=None,
                                  issue_datetime=None, nonce=None, issuer=None):
        """
        Prepares a provider access token response.

        Note:
            We only override this method to force the JWS class to use the HS256 algorithm.
        """

        body = {'access_token': 'foobar', 'token_type': 'bearer'}
        client_key = client_key or self.client_key
        now = datetime.datetime.utcnow()
        expiration_datetime = expiration_datetime or (now + datetime.timedelta(seconds=30))
        issue_datetime = issue_datetime or now
        nonce = nonce or 'a-nonce'
        issuer = issuer or self.issuer
        id_token = self.get_id_token(
            client_key, timegm(expiration_datetime.utctimetuple()),
            timegm(issue_datetime.utctimetuple()), nonce, issuer)

        body['id_token'] = JWS(id_token, jwk=self.key, alg='HS256').sign_compact()
        if tamper_message:
            header, msg, sig = body['id_token'].split('.')
            id_token['sub'] = '1235'
            msg = b64encode_item(id_token).decode('utf-8')
            body['id_token'] = '.'.join([header, msg, sig])

        return json.dumps(body)

    @pytest.mark.django_db(transaction=False)
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
            headers = {
                'Authorization': '{token_type} {token}'.format(token_type=expected_token_type,
                                                               token=self.fake_access_token)
            }
            mock_get_json.assert_called_once_with(self.backend.USER_INFO_URL, headers=headers)

    def test_logout_url(self):
        """ Verify the property returns the configured logout URL. """
        self.assertEqual(self.backend.logout_url, self.logout_url)

    def test_authorization_url(self):
        """ Verify the method utilizes the public URL, if one is set. """
        authorize_path = '/authorize/'
        self.assertEqual(self.backend.AUTHORIZATION_URL, self.url_root + authorize_path)

        expected = 'http://public.example.com'
        # NOTE (CCB): We use the strategy's method, rather than override_settings, because the TestStrategy
        # class being used does not rely on Django settings.
        self.strategy.set_settings({'SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT': expected})
        self.assertEqual(self.backend.AUTHORIZATION_URL, expected + authorize_path)

    def test_deprecated(self):
        """ Attempts to instantiate EdXOpenIdConnect should fire a warning. """
        with mock.patch('warnings.warn') as mock_warn:
            EdXOpenIdConnect(self.strategy, redirect_uri=self.complete_url)
            mock_warn.assert_called_once_with(
                'EdXOpenIdConnect is deprecated. Please use EdXOAuth2.', DeprecationWarning
            )


class EdXOAuth2Tests(OAuth2Test):
    """ Tests for the EdXOAuth2 backend. """

    backend_path = 'auth_backends.backends.EdXOAuth2'
    client_key = 'a-key'
    client_secret = 'a-secret-key'
    expected_username = 'jsmith'
    hmac_key = SYMKey(key='fake-key')
    openid_config_body = {
        'access_token_signing_alg_values_supported': [
            'RS512',
            'HS256'
        ],
        'claims_supported': [
            'sub',
            'iss',
            'name',
            'given_name',
            'family_name',
            'email'
        ],
        'token_endpoint': 'https://example.com/oauth2/access_token',
        'token_endpoint_auth_methods_supported': [
            'client_secret_post'
        ],
        'jwks_uri': 'https://example.com/oauth2/jwks.json',
        'end_session_endpoint': 'https://example.com/logout',
        'authorization_endpoint': 'https://example.com/oauth2/authorize',
        'scopes_supported': [
            'openid',
            'profile',
            'email'
        ],
        'issuer': 'https://example.com/oauth2'
    }
    provider_endpoint = 'https://example.com/oauth2'

    def setUp(self):
        cache.clear()
        super(EdXOAuth2Tests, self).setUp()
        self.key = RSAKey(kid='testkey', key=RSA.generate(2048))

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.provider_endpoint + '/.well-known/openid-configuration',
            status=200,
            body=json.dumps(self.openid_config_body)
        )

        provider_keys = KEYS()
        provider_keys.add(self.key.serialize())

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.openid_config_body['jwks_uri'],
            status=200,
            body=provider_keys.dump_jwks()
        )

    def access_token_body(self, request, _url, headers):  # pylint: disable=method-hidden,unused-argument
        """ Generates a response from the provider's access token endpoint. """
        # The backend should always request JWT access tokens, not Bearer.
        body = six.moves.urllib.parse.parse_qs(request.body.decode('utf8'))
        self.assertEqual(body['token_type'], ['jwt'])

        expires_in = 3600
        access_token = self.create_jws_access_token(expires_in)
        body = json.dumps({
            'scope': 'read write profile email',
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
        issuer = issuer or self.openid_config_body['issuer']
        payload = {
            'iss': issuer,
            'administrator': False,
            'iat': timegm(issue_datetime.utctimetuple()),
            'given_name': 'Joe',
            'sub': 'e3bfe0e4e7c6693efba9c3a93ee7f31b',
            'preferred_username': self.expected_username,
            'aud': 'InkocujLikyucsEdwiWatdebrEackmevLakDuifKooshkakWow',
            'scopes': ['read', 'write', 'profile', 'email'],
            'email': 'jsmith@example.com',
            'exp': timegm(expiration_datetime.utctimetuple()),
            'name': 'Joe Smith',
            'family_name': 'Smith'
        }
        access_token = JWS(payload, jwk=key, alg=alg).sign_compact()
        return access_token

    def extra_settings(self):
        settings = super(EdXOAuth2Tests, self).extra_settings()
        settings.update({
            'SOCIAL_AUTH_{0}_KEY'.format(self.name): self.client_key,
            'SOCIAL_AUTH_{0}_SECRET'.format(self.name): self.client_secret,
            'SOCIAL_AUTH_{0}_ENDPOINT'.format(self.name): self.provider_endpoint,
            'SOCIAL_AUTH_{0}_JWS_HMAC_SIGNING_KEY'.format(self.name): self.hmac_key.key,

        })
        return settings

    def test_login(self):
        self.do_login()

    def test_partial_pipeline(self):
        self.do_partial_pipeline()

    def test_end_session_url(self):
        """ The method should return the provider's logout URL. """
        self.assertEqual(self.backend.end_session_url(), self.openid_config_body['end_session_endpoint'])

    def test_invalid_issuer(self):
        """ AuthTokenError should be raised if the access token's issuer is incorrect. """
        access_token = self.create_jws_access_token(issuer='other-issuer')

        expected_msg = 'Token error: Invalid issuer. Expected {}. Received other-issuer.'.format(
            self.openid_config_body['issuer']
        )
        with self.assertRaisesRegex(AuthTokenError, expected_msg):
            self.backend.user_data(access_token)

    def test_expired_access_token(self):
        """ AuthTokenError should be raised if the issued access token is expired. """
        access_token = self.create_jws_access_token(expires_in=-3600)
        with self.assertRaisesRegex(AuthTokenError, 'Access token has expired'):
            self.backend.user_data(access_token)

    def test_hmac_signing_key(self):
        """ The backend should support HMAC signing keys in addition to asymmetric. """
        access_token = self.create_jws_access_token(key=self.hmac_key, alg='HS512')
        self.backend.user_data(access_token)

    def test_provider_configuration_caching(self):
        """ The provider configuration data should be cached by default. """
        cache.clear()
        self.assertEqual(self.backend.provider_configuration(), self.openid_config_body)

        HTTPretty.disable()
        self.assertEqual(self.backend.provider_configuration(), self.openid_config_body)

    def test_get_jwks_keys_caching(self):
        """ The JWKS keys should be cached by default. """
        expected = KEYS()
        expected.add(self.key.serialize())
        expected.add(self.hmac_key.serialize())

        # NOTE: KEYS objects have no __eq__ method defined, so we compare their string representations,
        # which are JWK sets.
        self.assertEqual(str(self.backend.get_jwks_keys()), str(expected))

        HTTPretty.disable()
        self.assertEqual(str(self.backend.get_jwks_keys()), str(expected))
