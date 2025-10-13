"""Python-social-auth pipeline functions.

For more info visit https://python-social-auth.readthedocs.io/en/latest/pipeline.html.
"""
import logging
from django.contrib.auth import get_user_model
from edx_django_utils.monitoring import set_custom_attribute

logger = logging.getLogger(__name__)
User = get_user_model()


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
        # Check if usernames don't match
        username_mismatch = details_username != user_username

        # .. custom_attribute_name: update_email.username_mismatch
        # .. custom_attribute_description: Tracks whether there's a mismatch between
        #    the username in the social details and the user's actual username.
        #    True if usernames don't match, False if they match.
        set_custom_attribute('update_email.username_mismatch', username_mismatch)

        if username_mismatch:
            # Log warning about the mismatch
            logger.warning(
                "Username mismatch during email update. User username: %s, Details username: %s",
                user_username,
                details_username
            )

            # Skip email update due to username mismatch
            logger.warning(
                "Skipping email update for user %s due to username mismatch",
                user_username
            )
            return  # Exit without updating email

        # Proceed with email update only if usernames match
        email = details.get('email')
        if email and user.email != email:
            user.email = email
            strategy.storage.user.changed(user)

            # .. custom_attribute_name: update_email.email_updated
            # .. custom_attribute_description: Indicates that the user's email was
            #    actually updated during this pipeline execution.
            set_custom_attribute('update_email.email_updated', True)
