""" Tests for pipelines. """

from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from social_django.utils import load_strategy

from auth_backends.pipeline import get_user_if_exists, update_email

User = get_user_model()


class GetUserIfExistsPipelineTests(TestCase):
    """ Tests for the get_user_if_exists pipeline function. """

    def setUp(self):
        super().setUp()
        self.username = 'edx'
        self.details = {'username': self.username}

    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_no_user_exists(self, mock_debug_toggle, mock_set_attribute):
        """ Verify an empty dict is returned if no user exists. """
        mock_debug_toggle.return_value = False

        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.details_username', self.username)
        mock_set_attribute.assert_any_call('get_user_if_exists.user_provided', False)
        mock_set_attribute.assert_any_call('get_user_if_exists.debug_enabled', False)
        mock_set_attribute.assert_any_call('get_user_if_exists.user_found', False)

    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_existing_user(self, mock_debug_toggle, mock_set_attribute):
        """ Verify a dict with the user and extra details is returned if the user exists. """
        mock_debug_toggle.return_value = False
        user = User.objects.create(username=self.username)

        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {'is_new': False, 'user': user})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.details_username', self.username)
        mock_set_attribute.assert_any_call('get_user_if_exists.user_provided', False)
        mock_set_attribute.assert_any_call('get_user_if_exists.debug_enabled', False)
        mock_set_attribute.assert_any_call('get_user_if_exists.user_found', True)
        mock_set_attribute.assert_any_call('get_user_if_exists.found_user_id', user.id)

    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_get_user_if_exists_with_user_provided(self, mock_debug_toggle, mock_set_attribute):
        """ Verify only the details are returned if a user is passed to the function. """
        mock_debug_toggle.return_value = False
        user = User.objects.create(username=self.username)

        actual = get_user_if_exists(None, self.details, user=user)
        self.assertDictEqual(actual, {'is_new': False})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.details_username', self.username)
        mock_set_attribute.assert_any_call('get_user_if_exists.user_provided', True)
        mock_set_attribute.assert_any_call('get_user_if_exists.debug_enabled', False)
        mock_set_attribute.assert_any_call('get_user_if_exists.existing_user_username', self.username)
        mock_set_attribute.assert_any_call('get_user_if_exists.username_mismatch', False)

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_username_mismatch_with_provided_user(self, mock_debug_toggle, mock_set_attribute, mock_logger):
        """ Verify proper handling when there's a username mismatch with provided user. """
        mock_debug_toggle.return_value = False
        user = User.objects.create(username='existing_user')
        details = {'username': 'different_user'}

        actual = get_user_if_exists(None, details, user=user)
        self.assertDictEqual(actual, {'is_new': False})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.details_username', 'different_user')
        mock_set_attribute.assert_any_call('get_user_if_exists.user_provided', True)
        mock_set_attribute.assert_any_call('get_user_if_exists.existing_user_username', 'existing_user')
        mock_set_attribute.assert_any_call('get_user_if_exists.username_mismatch', True)

        # Verify warning was logged
        mock_logger.warning.assert_called_once_with(
            "Username mismatch in get_user_if_exists. Details username: %s, "
            "Existing user username: %s. This may indicate an authentication issue.",
            'different_user',
            'existing_user'
        )

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_debug_enabled_with_existing_user(self, mock_debug_toggle, mock_logger):
        """ Verify debug logging when DEBUG_GET_USER_IF_EXISTS toggle is enabled. """
        mock_debug_toggle.return_value = True
        user = User.objects.create(username=self.username)

        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {'is_new': False, 'user': user})

        # Verify debug logging
        mock_logger.info.assert_called_with(
            "get_user_if_exists: Found existing user with username '%s' (ID: %s)",
            self.username,
            user.id
        )

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_debug_enabled_no_user_found(self, mock_debug_toggle, mock_logger):
        """ Verify debug logging when no user is found and debug is enabled. """
        mock_debug_toggle.return_value = True

        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {})

        # Verify debug logging
        mock_logger.info.assert_called_with(
            "get_user_if_exists: No user found with username '%s'",
            self.username
        )

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_no_username_in_details(self, mock_debug_toggle, mock_set_attribute, mock_logger):
        """ Verify proper handling when no username is provided in details. """
        mock_debug_toggle.return_value = False
        details = {}  # No username

        actual = get_user_if_exists(None, details)
        self.assertDictEqual(actual, {})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.details_username', None)
        mock_set_attribute.assert_any_call('get_user_if_exists.no_username_in_details', True)

        # Verify warning was logged
        mock_logger.warning.assert_called_with("get_user_if_exists: No username provided in details")

    @patch('auth_backends.pipeline.User.objects.get')
    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_database_error_handling(self, mock_debug_toggle, mock_set_attribute, mock_logger, mock_user_get):
        """ Verify proper handling of unexpected database errors. """
        mock_debug_toggle.return_value = False
        mock_user_get.side_effect = Exception("Database connection error")

        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {})

        # Verify custom attributes were set
        mock_set_attribute.assert_any_call('get_user_if_exists.lookup_error', True)
        mock_set_attribute.assert_any_call('get_user_if_exists.error_message', "Database connection error")

        # Verify error was logged
        mock_logger.error.assert_called_with(
            "get_user_if_exists: Unexpected error during user lookup for username '%s': %s",
            self.username,
            "Database connection error"
        )

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.DEBUG_GET_USER_IF_EXISTS.is_enabled')
    def test_debug_enabled_with_username_mismatch(self, mock_debug_toggle, mock_logger):
        """ Verify debug and warning logging when username mismatch occurs with debug enabled. """
        mock_debug_toggle.return_value = True
        user = User.objects.create(username='existing_user')
        details = {'username': 'different_user'}

        actual = get_user_if_exists(None, details, user=user)
        self.assertDictEqual(actual, {'is_new': False})

        # Verify both info and warning logs were called
        mock_logger.info.assert_called_with(
            "get_user_if_exists: User already provided. Username mismatch: %s. "
            "Details username: %s, Existing user username: %s",
            True,
            'different_user',
            'existing_user'
        )

        mock_logger.warning.assert_called_with(
            "Username mismatch in get_user_if_exists. Details username: %s, "
            "Existing user username: %s. This may indicate an authentication issue.",
            'different_user',
            'existing_user'
        )


class UpdateEmailPipelineTests(TestCase):
    """ Tests for the update_email pipeline function. """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='test_user')
        self.strategy = load_strategy()

    @patch('auth_backends.pipeline.SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email(self, mock_set_attribute, mock_toggle):
        """ Verify that user email is updated upon changing email when usernames match. """
        mock_toggle.return_value = False
        updated_email = 'updated@example.com'
        self.assertNotEqual(self.user.email, updated_email)

        initial_email = self.user.email

        update_email(self.strategy, {'email': updated_email, 'username': 'test_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, updated_email)
        self.assertNotEqual(updated_user.email, initial_email)

        mock_set_attribute.assert_any_call('update_email.username_mismatch', False)
        mock_set_attribute.assert_any_call('update_email.rollout_toggle_enabled', False)
        self.assert_attribute_was_set(mock_set_attribute, 'update_email.email_updated', should_exist=True)

    @patch('auth_backends.pipeline.SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email_with_none(self, mock_set_attribute, mock_toggle):
        """ Verify that user email is not updated if email value is None. """
        mock_toggle.return_value = False
        old_email = self.user.email

        update_email(self.strategy, {'email': None, 'username': 'test_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, old_email)

        mock_set_attribute.assert_any_call('update_email.username_mismatch', False)
        mock_set_attribute.assert_any_call('update_email.rollout_toggle_enabled', False)
        self.assert_attribute_was_set(mock_set_attribute, 'update_email.email_updated', should_exist=False)

    @patch('auth_backends.pipeline.SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled')
    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_username_mismatch_no_update_toggle_enabled(self, mock_set_attribute, mock_logger, mock_toggle):
        """ Verify that email is not updated when usernames don't match and toggle is enabled. """
        mock_toggle.return_value = True

        old_email = self.user.email
        updated_email = 'updated@example.com'

        update_email(self.strategy, {'email': updated_email, 'username': 'different_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, old_email)

        self.assertEqual(mock_logger.warning.call_count, 2)
        mock_logger.warning.assert_any_call(
            "Username mismatch during email update. User username: %s, Details username: %s",
            'test_user', 'different_user'
        )
        mock_logger.warning.assert_any_call(
            "Skipping email update for user %s due to username mismatch and "
            "SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH toggle enabled",
            'test_user'
        )

        mock_set_attribute.assert_any_call('update_email.username_mismatch', True)
        mock_set_attribute.assert_any_call('update_email.rollout_toggle_enabled', True)
        mock_set_attribute.assert_any_call('update_email.details_username', 'different_user')
        mock_set_attribute.assert_any_call('update_email.user_username', 'test_user')
        mock_set_attribute.assert_any_call('update_email.details_has_email', True)
        self.assert_attribute_was_set(mock_set_attribute, 'update_email.email_updated', should_exist=False)

    @patch('auth_backends.pipeline.SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled')
    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_username_mismatch_with_update_toggle_disabled(self, mock_set_attribute, mock_logger, mock_toggle):
        """ Verify that email is updated when usernames don't match but toggle is disabled. """
        mock_toggle.return_value = False

        old_email = self.user.email
        updated_email = 'updated@example.com'

        update_email(self.strategy, {'email': updated_email, 'username': 'different_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, updated_email)
        self.assertNotEqual(updated_user.email, old_email)

        mock_logger.warning.assert_called_once()

        mock_set_attribute.assert_any_call('update_email.username_mismatch', True)
        mock_set_attribute.assert_any_call('update_email.rollout_toggle_enabled', False)
        mock_set_attribute.assert_any_call('update_email.details_username', 'different_user')
        mock_set_attribute.assert_any_call('update_email.user_username', 'test_user')
        mock_set_attribute.assert_any_call('update_email.details_has_email', True)
        self.assert_attribute_was_set(mock_set_attribute, 'update_email.email_updated', should_exist=True)

    def assert_attribute_was_set(self, mock_set_attribute, attribute_name, should_exist=True):
        """ Assert that a specific attribute was or was not set via set_custom_attribute. """
        matching_calls = [
            call for call in mock_set_attribute.call_args_list
            if call[0][0] == attribute_name
        ]

        if should_exist:
            self.assertGreater(
                len(matching_calls), 0,
                f"Expected '{attribute_name}' to be set, but it wasn't"
            )
        else:
            self.assertEqual(
                len(matching_calls), 0,
                f"Expected '{attribute_name}' not to be set, but it was: {matching_calls}"
            )
