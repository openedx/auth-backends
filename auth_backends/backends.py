"""Django authentication backends.

For more information visit https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""
import datetime
import json
import warnings
from calendar import timegm

import six
from django.conf import settings
from django.core.cache import cache
from django.dispatch import Signal
from jwkest.jwk import KEYS
from jwkest.jws import JWS
from social_core.backends.oauth import BaseOAuth2
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.exceptions import AuthTokenError


# pylint: disable=abstract-method,missing-docstring
class EdXBackendMixin(object):
    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = ['profile', 'email']
    ID_KEY = 'preferred_username'
    PROFILE_TO_DETAILS_KEY_MAP = {
        'preferred_username': 'username',
        'email': 'email',
        'name': 'full_name',
        'given_name': 'first_name',
        'family_name': 'last_name',
        'locale': 'language',
        'user_tracking_id': 'user_tracking_id',
    }

    def get_user_details(self, response):
        details = self._map_user_details(response)

        # Limits the scope of languages we can use
        locale = response.get('locale')
        if locale:
            details['language'] = _to_language(response['locale'])

        # Set superuser bit if the provider determines the user is an administrator
        details['is_superuser'] = details['is_staff'] = response.get('administrator', False)

        return details

    def _map_user_details(self, response):
        """Maps key/values from the response to key/values in the user model.

        Does not transfer any key/value that is empty or not present in the response.
        """
        dest = {}
        for source_key, dest_key in self.PROFILE_TO_DETAILS_KEY_MAP.items():
            value = response.get(source_key)
            if value is not None:
                dest[dest_key] = value

        return dest


class EdXOpenIdConnect(EdXBackendMixin, OpenIdConnectAuth):
    """ DEPRECATED: OpenID Connect backend designed for use with the Open edX auth provider. """
    name = 'edx-oidc'

    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    ID_KEY = 'preferred_username'

    # Store the token type to ensure that we use the correct authentication mechanism for future calls.
    EXTRA_DATA = OpenIdConnectAuth.EXTRA_DATA + ['token_type']

    DEFAULT_SCOPE = ['openid', 'profile', 'email'] + getattr(settings, 'EXTRA_SCOPE', [])

    PROFILE_TO_DETAILS_KEY_MAP = {
        'preferred_username': 'username',
        'email': 'email',
        'name': 'full_name',
        'given_name': 'first_name',
        'family_name': 'last_name',
        'locale': 'language',
        'user_tracking_id': 'user_tracking_id',
    }

    auth_complete_signal = Signal(providing_args=['user', 'id_token'])

    def __init__(self, *args, **kwargs):
        super(EdXOpenIdConnect, self).__init__(*args, **kwargs)
        warnings.warn('EdXOpenIdConnect is deprecated. Please use EdXOAuth2.', DeprecationWarning)

    def get_jwks_keys(self):
        """ Returns the keys used to decode the ID token.

        Note:
            edX uses symmetric keys, so bypass the parent class's calls to an external
            server and return the key from settings.
        """
        keys = KEYS()
        keys.add({'key': self.setting('ID_TOKEN_DECRYPTION_KEY'), 'kty': 'oct'})
        return keys

    @property
    def ID_TOKEN_ISSUER(self):  # pylint: disable=invalid-name
        """ Expected value of the `iss` claim in the ID token. """
        return self.setting('ISSUER')

    @property
    def OIDC_ENDPOINT(self):  # pylint: disable=invalid-name
        """ OpenID Connect discovery endpoint. """
        url_root = self.setting('PUBLIC_URL_ROOT')

        if not url_root:
            url_root = self.setting('URL_ROOT')

        return url_root

    @property
    def AUTHORIZATION_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's authorization endpoint. """
        url_root = self.setting('PUBLIC_URL_ROOT')

        if not url_root:
            url_root = self.setting('URL_ROOT')

        return '{}/authorize/'.format(url_root)

    @property
    def ACCESS_TOKEN_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's access token endpoint. """
        return '{}/access_token/'.format(self.setting('URL_ROOT'))

    @property
    def USER_INFO_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's user info endpoint. """
        return '{}/user_info/'.format(self.setting('URL_ROOT'))

    @property
    def logout_url(self):
        """ URL of the auth provider's logout page. """
        return self.setting('LOGOUT_URL')

    def user_data(self, _access_token, *_args, **_kwargs):
        # Include decoded id_token fields in user data.
        return self.id_token

    def auth_complete_params(self, state=None):
        params = super(EdXOpenIdConnect, self).auth_complete_params(state)

        # TODO: Due a limitation in the OIDC provider in the LMS, the list of all course permissions
        # is computed during the authentication process. As an optimization, we explicitly request
        # the list here, avoiding further roundtrips. This is no longer necessary once the limitation
        # is resolved and instead the course permissions can be requested on a need to have basis,
        # reducing overhead significantly.
        claim_names = getattr(settings, 'COURSE_PERMISSIONS_CLAIMS', [])
        courses_claims_request = {name: {'essential': True} for name in claim_names}
        params['claims'] = json.dumps({'id_token': courses_claims_request})

        return params

    def auth_complete(self, *args, **kwargs):
        # WARNING: During testing, the user model class is `social_core.tests.models.User`,
        # not the model specified for the application.
        user = super(EdXOpenIdConnect, self).auth_complete(*args, **kwargs)
        self.auth_complete_signal.send(sender=self.__class__, user=user, id_token=self.id_token)
        return user

    def get_user_claims(self, access_token, claims=None, token_type='Bearer'):
        """Returns a dictionary with the values for each claim requested."""
        data = self.get_json(
            self.USER_INFO_URL,
            headers={'Authorization': '{token_type} {token}'.format(token_type=token_type, token=access_token)}
        )

        if claims:
            claims_names = set(claims)
            data = {k: v for (k, v) in six.iteritems(data) if k in claims_names}

        return data

    # NOTE (CCB): We are TEMPORARILY disabling the nonce validation while we transition our
    # authentication provider to properly implement storing the nonce at the point of initial
    # authorization, rather than when we request the access token.
    def auth_params(self, state=None):
        return super(OpenIdConnectAuth, self).auth_params(state)  # pylint: disable=bad-super-call

    def validate_claims(self, id_token):
        if id_token['iss'] != self.id_token_issuer():
            raise AuthTokenError(self, 'Invalid issuer')

        client_id, __ = self.get_key_and_secret()

        if isinstance(id_token['aud'], six.string_types):
            id_token['aud'] = [id_token['aud']]

        if client_id not in id_token['aud']:
            raise AuthTokenError(self, 'Invalid audience')

        if len(id_token['aud']) > 1 and 'azp' not in id_token:
            raise AuthTokenError(self, 'Incorrect id_token: azp')

        if 'azp' in id_token and id_token['azp'] != client_id:
            raise AuthTokenError(self, 'Incorrect id_token: azp')

        utc_timestamp = timegm(datetime.datetime.utcnow().utctimetuple())
        if utc_timestamp > id_token['exp']:
            raise AuthTokenError(self, 'Signature has expired')

        if 'nbf' in id_token and utc_timestamp < id_token['nbf']:
            raise AuthTokenError(self, 'Incorrect id_token: nbf')

        # Verify the token was issued in the last 10 minutes
        iat_leeway = self.setting('ID_TOKEN_MAX_AGE', self.ID_TOKEN_MAX_AGE)
        if utc_timestamp > id_token['iat'] + iat_leeway:
            raise AuthTokenError(self, 'Incorrect id_token: iat')

            # Validate the nonce to ensure the request was not modified
            # nonce = id_token.get('nonce')
            # if not nonce:
            #     raise AuthTokenError(self, 'Incorrect id_token: nonce')
            #
            # nonce_obj = self.get_nonce(nonce)
            # if nonce_obj:
            #     self.remove_nonce(nonce_obj.id)
            # else:
            #     raise AuthTokenError(self, 'Incorrect id_token: nonce')


def _to_language(locale):
    """Convert locale name to language code if necessary.

    OpenID Connect locale needs to be converted to Django's language
    code. In general however, the differences between the locale names
    and language code are not very clear among different systems.

    For more information, refer to:
        http://openid.net/specs/openid-connect-basic-1_0.html#StandardClaims
        https://docs.djangoproject.com/en/1.6/topics/i18n/#term-translation-string
    """
    return locale.replace('_', '-').lower()


class EdXOAuth2(EdXBackendMixin, BaseOAuth2):
    name = 'edx-oauth2'

    def endpoint(self):
        return self.setting('ENDPOINT').strip('/')

    def provider_configuration(self):
        cache_key = 'edx_oauth2_provider_configuration'
        config = cache.get(cache_key)

        if not config:
            config = self.get_json(self.endpoint() + '/.well-known/openid-configuration')

            # Cache for one week since the configuration rarely changes
            cache.set(cache_key, config, self.setting('PROVIDER_CONFIGURATION_CACHE_TTL', 604800))

        return config

    def authorization_url(self):
        return self.provider_configuration().get('authorization_endpoint')

    def access_token_url(self):
        return self.provider_configuration().get('token_endpoint')

    def end_session_url(self):
        return self.provider_configuration().get('end_session_endpoint')

    def jwt_issuer(self):
        return self.provider_configuration().get('issuer')

    def jwks_uri(self):
        return self.provider_configuration().get('jwks_uri')

    def get_jwks_keys(self):
        cache_key = 'edx_oauth2_jwks'
        keys = KEYS()
        jwks = cache.get(cache_key)

        # KEYS objects cannot be cached since they cannot be pickled. Therefore we cache the parsed JWKS
        # response from the server since it is a string.
        if jwks:
            keys.load_jwks(jwks)
        else:
            keys.load_from_url(self.jwks_uri())
            jwks = keys.dump_jwks()

            # Cache for one day to account for key rotations
            cache.set(cache_key, jwks, self.setting('JWKS_CACHE_TTL', 86400))

        # Retain support for HMAC signing.
        # Don't cache this since the frequency of its changes are not defined, and we don't necessarily want
        # to force a cache clear every time the settings are changed/service deployed.
        hmac_secret = self.setting('JWS_HMAC_SIGNING_KEY', None)

        if hmac_secret:
            keys.add({'key': hmac_secret, 'kty': 'oct'})

        return keys

    def auth_complete_params(self, state=None):
        params = super(EdXOAuth2, self).auth_complete_params(state)
        # Request a JWT access token containing the user info
        params['token_type'] = 'jwt'
        return params

    def user_data(self, access_token, *args, **kwargs):
        access_token = JWS().verify_compact(access_token.encode('utf-8'), self.get_jwks_keys())

        expected_issuer = self.jwt_issuer()
        actual_issuer = access_token['iss']
        if actual_issuer != expected_issuer:
            error_msg = 'Invalid issuer. Expected {expected}. Received {actual}.'.format(
                expected=expected_issuer, actual=actual_issuer
            )
            raise AuthTokenError(self, error_msg)

        utc_timestamp = timegm(datetime.datetime.utcnow().utctimetuple())
        if utc_timestamp > access_token['exp']:
            raise AuthTokenError(self, 'Access token has expired')

        keys = list(self.PROFILE_TO_DETAILS_KEY_MAP.keys()) + ['administrator']
        user_data = {key: access_token[key] for key in keys if key in access_token}
        return user_data
