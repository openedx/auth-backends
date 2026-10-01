"""Django authentication backends.

For more information visit https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""
import logging
import jwt
from django.contrib.auth import logout
from django.dispatch import Signal
from social_core.backends.oauth import BaseOAuth2
from edx_django_utils.monitoring import set_custom_attribute

logger = logging.getLogger(__name__)

PROFILE_CLAIMS_TO_DETAILS_KEY_MAP = {
    'preferred_username': 'username',
    'email': 'email',
    'name': 'full_name',
    'given_name': 'first_name',
    'family_name': 'last_name',
    'locale': 'language',
    'user_id': 'user_id',
}


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


class EdXOAuth2(BaseOAuth2):
    """
    IMPORTANT: The oauth2 application must have access to the ``user_id`` scope in order
    to use this backend.
    """
    # used by social-auth
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'preferred_username'

    name = 'edx-oauth2'

    DEFAULT_SCOPE = ['user_id', 'profile', 'email']
    discard_missing_values = True
    # EXTRA_DATA is used to store important data in the UserSocialAuth.extra_data field.
    # See https://python-social-auth.readthedocs.io/en/latest/backends/oauth.html?highlight=extra_data
    EXTRA_DATA = [
        # Update the stored user_id, if it's present in the response
        ('user_id', 'user_id', discard_missing_values),
        # Update the stored refresh_token, if it's present in the response
        ('refresh_token', 'refresh_token', discard_missing_values),
    ]

    # local only (not part of social-auth)
    CLAIMS_TO_DETAILS_KEY_MAP = PROFILE_CLAIMS_TO_DETAILS_KEY_MAP

    # This signal is fired after the user has successfully logged in.
    # providing_args=['user']
    auth_complete_signal = Signal()

    @property
    # pylint: disable= missing-function-docstring
    def logout_url(self):
        if self.setting('LOGOUT_REDIRECT_URL'):
            return f"{self.end_session_url()}?client_id={self.setting('KEY')}&" \
                   f"redirect_url={self.setting('LOGOUT_REDIRECT_URL')}"
        else:
            return self.end_session_url()

    def start(self):
        """Initialize OAuth authentication with session cleanup."""

        request = self.strategy.request if hasattr(self.strategy, 'request') else None

        user_authenticated = (
            request is not None and
            hasattr(request, 'user') and
            request.user.is_authenticated
        )

        # .. custom_attribute_name: session_cleanup.logout_required
        # .. custom_attribute_description: Tracks whether a user was authenticated
        #    before session cleanup. True if user was logged in, False otherwise.
        set_custom_attribute('session_cleanup.logout_required', user_authenticated)

        if user_authenticated:
            existing_username = getattr(request.user, 'username', 'unknown')

            logger.info(
                "OAuth start: Performing session cleanup for user '%s'",
                existing_username
            )

            logout(request)

        return super().start()

    def authorization_url(self):
        url_root = self.get_public_or_internal_url_root()
        return f'{url_root}/oauth2/authorize'

    def access_token_url(self):
        return f"{self.setting('URL_ROOT')}/oauth2/access_token"

    def end_session_url(self):
        url_root = self.get_public_or_internal_url_root()
        return f'{url_root}/logout'

    def auth_complete_params(self, state=None):
        params = super().auth_complete_params(state)
        # Request a JWT access token containing the user info
        params['token_type'] = 'jwt'
        return params

    def auth_complete(self, *args, **kwargs):
        """
        This method is overwritten to emit the `EdXOAuth2.auth_complete_signal` signal.
        """
        # WARNING: During testing, the user model class is `social_core.tests.models.User`,
        # not the model specified for the application.
        user = super().auth_complete(*args, **kwargs)
        self.auth_complete_signal.send(sender=self.__class__, user=user)
        return user

    def user_data(self, access_token, *args, **kwargs):
        # The algorithm is required but unused because signature verification is skipped.
        # Note: signature verification happens earlier during the authentication process.
        decoded_access_token = jwt.decode(access_token, algorithms=["HS256"], options={"verify_signature": False})
        keys = list(self.CLAIMS_TO_DETAILS_KEY_MAP.keys()) + ['administrator', 'superuser']
        user_data = {key: decoded_access_token[key] for key in keys if key in decoded_access_token}
        return user_data

    def get_user_details(self, response):
        details = self._map_user_details(response)

        # Limits the scope of languages we can use
        locale = response.get('locale')
        if locale:
            details['language'] = _to_language(response['locale'])

        details['is_staff'] = response.get('administrator', False)
        details['is_superuser'] = response.get('superuser', False)

        return details

    def get_public_or_internal_url_root(self):
        return self.setting('PUBLIC_URL_ROOT') or self.setting('URL_ROOT')

    def _map_user_details(self, response):
        """Maps key/values from the response to key/values in the user model.

        Does not transfer any key/value that is empty or not present in the response.
        """
        dest = {}
        for source_key, dest_key in self.CLAIMS_TO_DETAILS_KEY_MAP.items():
            value = response.get(source_key)
            if value is not None:
                dest[dest_key] = value

        return dest
