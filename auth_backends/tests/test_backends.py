""" Tests for the backends. """
import datetime
import json
import unittest
from calendar import timegm

import ddt
import mock
import pytest
import six
from auth_backends.strategies import EdxDjangoStrategy
from jwkest.jwk import SYMKey
from jwkest.jws import JWS
from jwkest.jwt import b64encode_item
from social_core.tests.backends.oauth import OAuth2Test
from social_core.tests.backends.open_id_connect import OpenIdConnectTestMixin


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
    def access_token_body(self, request, _url, headers):    # pylint: disable=method-hidden
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
