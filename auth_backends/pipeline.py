"""Python-social-auth pipeline functions.

For more info visit https://python-social-auth.readthedocs.io/en/latest/pipeline.html.
"""
import logging
from django.contrib.auth import get_user_model
from edx_toggles.toggles import SettingToggle
from edx_django_utils.monitoring import set_custom_attribute

logger = logging.getLogger(__name__)
User = get_user_model()

# .. toggle_name: SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH
# .. toggle_implementation: SettingToggle
# .. toggle_default: False
# .. toggle_description: Determines whether to block email updates when usernames don't match.
#    When enabled (True), email updates will be blocked when the username in social auth details
#    doesn't match the user's username. When disabled (False), email updates will proceed regardless
#    of username mismatches. This will be used for a temporary rollout.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2025-06-18
# .. toggle_target_removal_date: 2025-08-18
SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH = SettingToggle("SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH", default=False)

# .. toggle_name: IGNORE_LOGGED_IN_USER_ON_MISMATCH
# .. toggle_implementation: SettingToggle
# .. toggle_default: True
# .. toggle_description: Controls behavior when there's a username mismatch between the logged-in user
#    and social auth details. When enabled (True), ignores the logged-in user and proceeds with
#    user lookup from social auth details. When disabled (False), proceeds with the logged-in user
#    despite the mismatch. This toggle is for temporary rollout only to ensure we don't create bugs.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2025-07-25
# .. toggle_target_removal_date: 2025-09-25
IGNORE_LOGGED_IN_USER_ON_MISMATCH = SettingToggle("IGNORE_LOGGED_IN_USER_ON_MISMATCH", default=True)


# pylint: disable=unused-argument
# The function parameters must be named exactly as they are below.
# Do not change them to appease Pylint.
def get_user_if_exists(strategy, details, user=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """
    Return a User with the given username iff the User exists.
    """
    # .. custom_attribute_name: get_user_if_exists.ignore_toggle_enabled
    # .. custom_attribute_description: Tracks whether the IGNORE_LOGGED_IN_USER_ON_MISMATCH
    #    toggle is enabled during this pipeline execution.
    set_custom_attribute('get_user_if_exists.ignore_toggle_enabled', IGNORE_LOGGED_IN_USER_ON_MISMATCH.is_enabled())

    if user:
        # Check for username mismatch and toggle behavior
        details_username = details.get('username')
        user_username = getattr(user, 'username', None)

        # .. custom_attribute_name: get_user_if_exists.has_details_username
        # .. custom_attribute_description: Tracks whether the details contain a username field.
        #    True if username is present and not None, False if username is missing or None.
        set_custom_attribute('get_user_if_exists.has_details_username', bool(details_username))

        username_mismatch = details_username != user_username

        # .. custom_attribute_name: get_user_if_exists.username_mismatch
        # .. custom_attribute_description: Tracks whether there's a mismatch between
        #    the username in the social details and the user's actual username.
        #    True if usernames don't match, False if they match.
        set_custom_attribute('get_user_if_exists.username_mismatch', username_mismatch)

        if username_mismatch and IGNORE_LOGGED_IN_USER_ON_MISMATCH.is_enabled():
            logger.info(
                "Username mismatch detected. Username from Details: %s, Username from User: %s.",
                details_username, user_username
            )
        else:
            return {'is_new': False}

    try:
        username = details.get('username')

        return {
            'is_new': False,
            'user': User.objects.get(username=username)
        }
    except User.DoesNotExist:
        pass

    return {}


def update_email(strategy, details, user=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Update the user's email address using data from provider."""

    if user:
        # Get usernames for comparison, using defensive coding
        details_username = details.get('username')
        user_username = getattr(user, 'username', None)
        # Check if usernames don't match
        username_mismatch = details_username != user_username

        # .. custom_attribute_name: update_email.username_mismatch
        # .. custom_attribute_description: Tracks whether there's a mismatch between
        #    the username in the social details and the user's actual username.
        #    True if usernames don't match, False if they match.
        set_custom_attribute('update_email.username_mismatch', username_mismatch)

        # .. custom_attribute_name: update_email.rollout_toggle_enabled
        # .. custom_attribute_description: Tracks whether the SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH
        #    toggle is enabled during this pipeline execution.
        set_custom_attribute('update_email.rollout_toggle_enabled', SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled())

        if username_mismatch:
            # Log warning and set additional custom attributes for mismatches
            logger.warning(
                "Username mismatch during email update. User username: %s, Details username: %s",
                user_username,
                details_username
            )
            # .. custom_attribute_name: update_email.details_username
            # .. custom_attribute_description: Records the username provided in the
            #    social details when a mismatch occurs with the user's username.
            set_custom_attribute('update_email.details_username', details_username)

            # .. custom_attribute_name: update_email.user_username
            # .. custom_attribute_description: Records the actual username of the user
            #    when a mismatch occurs with the social details username.
            set_custom_attribute('update_email.user_username', user_username)

            # .. custom_attribute_name: update_email.details_has_email
            # .. custom_attribute_description: Records whether the details contain an email
            #    when a username mismatch occurs, to identify potential edge cases.
            set_custom_attribute('update_email.details_has_email', bool(details.get('email')))

            # Only exit if the toggle is enabled
            if SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled():
                logger.warning(
                    "Skipping email update for user %s due to username mismatch and "
                    "SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH toggle enabled",
                    user_username
                )
                return  # Exit without updating email

        # Proceed with email update only if usernames match or toggle is disabled
        email = details.get('email')
        if email and user.email != email:
            user.email = email
            strategy.storage.user.changed(user)

            # .. custom_attribute_name: update_email.email_updated
            # .. custom_attribute_description: Indicates that the user's email was
            #    actually updated during this pipeline execution.
            set_custom_attribute('update_email.email_updated', True)
