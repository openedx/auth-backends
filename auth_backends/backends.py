"""Django authentication backends.

For more information visit https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""
import json

from django.conf import settings
import django.dispatch
import six
from social.backends.open_id import OpenIdConnectAuth


# pylint: disable=abstract-method
class EdXOpenIdConnect(OpenIdConnectAuth):
    """ OpenID Connect backend designed for use with the Open edX auth provider. """
    name = 'edx-oidc'

    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    ID_KEY = 'preferred_username'

    # Store the token type to ensure that we use the correct authentication mechanism for future calls.
    EXTRA_DATA = OpenIdConnectAuth.EXTRA_DATA + ['token_type']

    DEFAULT_SCOPE = ['openid', 'profile', 'email'] + getattr(settings, 'EXTRA_SCOPE', [])

    PROFILE_TO_DETAILS_KEY_MAP = {
        'preferred_username': u'username',
        'email': u'email',
        'name': u'full_name',
        'given_name': u'first_name',
        'family_name': u'last_name',
        'locale': u'language',
    }

    auth_complete_signal = django.dispatch.Signal(providing_args=['user', 'id_token'])

    @property
    def ID_TOKEN_ISSUER(self):  # pylint: disable=invalid-name
        """ Expected value of the `iss` claim in the ID token. """
        return self.setting('ISSUER')

    @property
    def AUTHORIZATION_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's authorization endpoint. """
        return '{0}/authorize/'.format(self.setting('URL_ROOT'))

    @property
    def ACCESS_TOKEN_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's access token endpoint. """
        return '{0}/access_token/'.format(self.setting('URL_ROOT'))

    @property
    def USER_INFO_URL(self):  # pylint: disable=invalid-name
        """ URL of the auth provider's user info endpoint. """
        return '{0}/user_info/'.format(self.setting('URL_ROOT'))

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
        # WARNING: During testing, the user model class is `social.tests.models` and not the one
        # specified for the application.
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

    def get_user_details(self, response):
        details = self._map_user_details(response)

        # Limits the scope of languages we can use
        locale = response.get('locale')
        if locale:
            details[u'language'] = _to_language(response['locale'])

        # Set superuser bit if the provider determines the user is an administrator
        details[u'is_superuser'] = details[u'is_staff'] = response.get('administrator', False)

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
