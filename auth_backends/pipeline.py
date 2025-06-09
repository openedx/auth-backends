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
#    of username mismatches.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2025-06-05
# .. toggle_target_removal_date: 2026-06-05
# .. toggle_warnings: This is a temporary toggle for a security enhancement rollout.
# .. toggle_tickets: ARCHBOM-2181
SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH = SettingToggle("SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH", default=False)


# pylint: disable=unused-argument
# The function parameters must be named exactly as they are below.
# Do not change them to appease Pylint.
def get_user_if_exists(strategy, details, user=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Return a User with the given username iff the User exists."""
    if user:
        return {'is_new': False}
    try:
        username = details.get('username')

        # Return the user if it exists
        return {
            'is_new': False,
            'user': User.objects.get(username=username)
        }
    except User.DoesNotExist:
        # Fall to the default return value
        pass

    # Nothing to return since we don't have a user
    return {}


def update_email(strategy, details, user=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Update the user's email address using data from provider."""
    if user:
        # Get usernames for comparison, using defensive coding
        details_username = details.get('username')
        user_username = getattr(user, 'username', None)
        # Check if usernames match
        username_match = details_username == user_username

        # .. custom_attribute_name: update_email.username_mismatch
        # .. custom_attribute_description: Tracks whether there's a mismatch between
        #    the username in the social details and the user's actual username.
        #    True if usernames don't match, False if they match.
        set_custom_attribute('update_email.username_mismatch', not username_match)

        if not username_match:
            # Log warning and set additional custom attributes for mismatches
            logger.warning(
                "Username mismatch during email update. User username: %s, Details username: %s",
                user_username,
                details_username
            )
            # .. custom_attribute_name: update_email.details_username
            # .. custom_attribute_description: Records the username provided in the
            #    social details when a mismatch occurs with the user's username.
            set_custom_attribute('update_email.details_username', str(details_username))

            # .. custom_attribute_name: update_email.user_username
            # .. custom_attribute_description: Records the actual username of the user
            #    when a mismatch occurs with the social details username.
            set_custom_attribute('update_email.user_username', str(user_username))

            # .. custom_attribute_name: update_email.details_has_email
            # .. custom_attribute_description: Records whether the details contain an email
            #    when a username mismatch occurs, to identify potential edge cases.
            set_custom_attribute('update_email.details_has_email', details.get('email') is not None)

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
