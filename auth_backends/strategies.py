"""
Python Social Auth strategies.

See http://python-social-auth.readthedocs.io/en/latest/strategies.html for more information.
"""

from social_django.strategy import DjangoStrategy


class EdxDjangoStrategy(DjangoStrategy):
    """
    Custom strategy for edX Django services.

    This strategy includes default settings that are standard across edX Django projects.

    In order to use this strategy, the value of the setting `SOCIAL_AUTH_STRATEGY` must be set to
    `'auth_backends.strategies.EdxDjangoStrategy'`.
    """
    DEFAULT_SETTINGS = {
        'SOCIAL_AUTH_PIPELINE': (
            'social_core.pipeline.social_auth.social_details',
            'social_core.pipeline.social_auth.social_uid',
            'social_core.pipeline.social_auth.auth_allowed',
            'social_core.pipeline.social_auth.social_user',

            # By default python-social-auth will simply create a new user/username if the username
            # from the provider conflicts with an existing username in this system. This custom pipeline function
            # loads existing users instead of creating new ones.
            'auth_backends.pipeline.get_user_if_exists',

            # social_core.pipeline.user.get_username is NOT used because the username should come from the JWS access
            # token or ID token. There is no need to create a new username.
            # 'social_core.pipeline.user.get_username',

            'social_core.pipeline.user.create_user',
            'social_core.pipeline.social_auth.associate_user',
            'social_core.pipeline.social_auth.load_extra_data',
            'social_core.pipeline.user.user_details',

            # social_core consider's email field protected and won't let it change,
            # added a new pipeline function to update email address.
            'auth_backends.pipeline.update_email'
        ),

        # Always raise auth exceptions so that they are properly logged. Otherwise, the PSA middleware will redirect to
        # an auth error page and attempt to display the error message to the user (via Django's message framework). We
        # do not want the user to see the message; but, we do want our downstream exception handlers to log the message.
        'SOCIAL_AUTH_RAISE_EXCEPTIONS': True,

        # Assume HTTPS unless explicitly overridden (e.g. for development)
        'SOCIAL_AUTH_REDIRECT_IS_HTTPS': True,

        # Fields passed to our custom user model when creating a new user
        'SOCIAL_AUTH_USER_FIELDS': ['username', 'email', 'first_name', 'last_name'],

        # Allow callers to not specify a value for this URL
        'LOGOUT_REDIRECT_URL': None,
    }

    def get_setting(self, name):
        try:
            return super(EdxDjangoStrategy, self).get_setting(name)
        # Throws AttributeError if the setting is undefined, and the setting name DOES NOT end with "_URL".
        # Throws TypeError if the setting is undefined, and the setting name DOES end with "_URL".
        #
        # Also, Throws TypeError for other TypeError reasons that we'd prefer not to capture, but the underlying
        # framework is not so flexible.
        except (AttributeError, TypeError):
            return self.DEFAULT_SETTINGS[name]
