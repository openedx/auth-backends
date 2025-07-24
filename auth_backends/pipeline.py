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

# .. toggle_name: DEBUG_GET_USER_IF_EXISTS
# .. toggle_implementation: SettingToggle
# .. toggle_default: False
# .. toggle_description: Enables detailed debugging and monitoring for the get_user_if_exists pipeline function.
#    When enabled (True), additional logging and custom attributes will be set to help debug
#    user account conflicts and authentication issues.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2025-07-23
# .. toggle_target_removal_date: 2025-09-23
DEBUG_GET_USER_IF_EXISTS = SettingToggle("DEBUG_GET_USER_IF_EXISTS", default=False)


# pylint: disable=unused-argument
# The function parameters must be named exactly as they are below.
# Do not change them to appease Pylint.
def get_user_if_exists(strategy, details, user=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Return a User with the given username iff the User exists.

    Enhanced with debugging capabilities to track user account conflicts and authentication issues.
    """
    details_username = details.get('username')

    # Set custom attributes for debugging
    # .. custom_attribute_name: get_user_if_exists.details_username
    # .. custom_attribute_description: Records the username provided in the social details
    #    to help debug authentication and user lookup issues.
    set_custom_attribute('get_user_if_exists.details_username', details_username)

    # .. custom_attribute_name: get_user_if_exists.user_provided
    # .. custom_attribute_description: Indicates whether a user object was already provided
    #    to the pipeline function, which affects the lookup logic.
    set_custom_attribute('get_user_if_exists.user_provided', user is not None)

    # .. custom_attribute_name: get_user_if_exists.debug_enabled
    # .. custom_attribute_description: Tracks whether the DEBUG_GET_USER_IF_EXISTS
    #    toggle is enabled during this pipeline execution.
    set_custom_attribute('get_user_if_exists.debug_enabled', DEBUG_GET_USER_IF_EXISTS.is_enabled())

    if user:
        # User is already provided - this typically happens when user exists from previous pipeline steps
        existing_username = getattr(user, 'username', None)

        # .. custom_attribute_name: get_user_if_exists.existing_user_username
        # .. custom_attribute_description: Records the username of the existing user object
        #    when a user is already provided to the pipeline.
        set_custom_attribute('get_user_if_exists.existing_user_username', existing_username)

        # Check for username mismatch between provided user and details
        username_mismatch = details_username != existing_username

        # .. custom_attribute_name: get_user_if_exists.username_mismatch
        # .. custom_attribute_description: Tracks whether there's a mismatch between
        #    the username in details and the existing user's username.
        set_custom_attribute('get_user_if_exists.username_mismatch', username_mismatch)

        if DEBUG_GET_USER_IF_EXISTS.is_enabled() or username_mismatch:
            logger.info(
                "get_user_if_exists: User already provided. Username mismatch: %s. "
                "Details username: %s, Existing user username: %s",
                username_mismatch,
                details_username,
                existing_username
            )

        if username_mismatch:
            logger.warning(
                "Username mismatch in get_user_if_exists. Details username: %s, "
                "Existing user username: %s. This may indicate an authentication issue.",
                details_username,
                existing_username
            )

        return {'is_new': False}

    # No user provided, attempt to find user by username from details
    if not details_username:
        logger.warning("get_user_if_exists: No username provided in details")
        # .. custom_attribute_name: get_user_if_exists.no_username_in_details
        # .. custom_attribute_description: Indicates that no username was provided in the details,
        #    which may indicate an issue with the authentication provider.
        set_custom_attribute('get_user_if_exists.no_username_in_details', True)
        return {}

    try:
        found_user = User.objects.get(username=details_username)

        # .. custom_attribute_name: get_user_if_exists.user_found
        # .. custom_attribute_description: Indicates that a user was successfully found
        #    by username lookup in the database.
        set_custom_attribute('get_user_if_exists.user_found', True)

        # .. custom_attribute_name: get_user_if_exists.found_user_id
        # .. custom_attribute_description: Records the ID of the user found by username lookup
        #    to help track user account conflicts.
        set_custom_attribute('get_user_if_exists.found_user_id', found_user.id)

        if DEBUG_GET_USER_IF_EXISTS.is_enabled():
            logger.info(
                "get_user_if_exists: Found existing user with username '%s' (ID: %s)",
                details_username,
                found_user.id
            )

        # Return the user if it exists
        return {
            'is_new': False,
            'user': found_user
        }
    except User.DoesNotExist:
        # .. custom_attribute_name: get_user_if_exists.user_found
        # .. custom_attribute_description: Indicates that no user was found
        #    by username lookup in the database.
        set_custom_attribute('get_user_if_exists.user_found', False)

        if DEBUG_GET_USER_IF_EXISTS.is_enabled():
            logger.info(
                "get_user_if_exists: No user found with username '%s'",
                details_username
            )

    except Exception as e:
        # Handle any unexpected errors during user lookup
        logger.error(
            "get_user_if_exists: Unexpected error during user lookup for username '%s': %s",
            details_username,
            str(e)
        )

        # .. custom_attribute_name: get_user_if_exists.lookup_error
        # .. custom_attribute_description: Indicates that an unexpected error occurred
        #    during user lookup, which may indicate database or system issues.
        set_custom_attribute('get_user_if_exists.lookup_error', True)

        # .. custom_attribute_name: get_user_if_exists.error_message
        # .. custom_attribute_description: Records the error message when an unexpected
        #    error occurs during user lookup.
        set_custom_attribute('get_user_if_exists.error_message', str(e))

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
