"""Python-social-auth pipeline functions.

For more info visit http://python-social-auth.readthedocs.org/en/latest/pipeline.html.
"""
from django.contrib.auth import get_user_model


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
        email = details.get('email')

        if email and user.email != email:
            user.email = email
            strategy.storage.user.changed(user)
