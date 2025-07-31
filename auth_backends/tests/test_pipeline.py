""" Tests for pipelines. """

from unittest.mock import patch
import ddt
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from social_django.utils import load_strategy

from auth_backends.pipeline import get_user_if_exists, update_email

User = get_user_model()


@ddt.ddt
class GetUserIfExistsPipelineTests(TestCase):
    """
    Tests for the get_user_if_exists pipeline function.
    """

    def setUp(self):
        super().setUp()
        self.username = 'edx'
        self.details = {'username': self.username}

    @ddt.data(True, False)
    def test_no_user_exists(self, setting_value):
        """
        Verify an empty dict is returned if no user exists regardless of setting.
        """
        with override_settings(IGNORE_LOGGED_IN_USER_ON_MISMATCH=setting_value):
            actual = get_user_if_exists(None, self.details)
            self.assertDictEqual(actual, {})

    @ddt.data(
        # (test_config, expected_result)
        ({'setting': True, 'user_provided': False, 'username_match': True, 'target_exists': True},
         {'is_new': False, 'user': 'found_user'}),  # setting=True, no current user
        ({'setting': False, 'user_provided': False, 'username_match': True, 'target_exists': True},
         {'is_new': False, 'user': 'found_user'}),  # setting=False, no current user
        ({'setting': True, 'user_provided': True, 'username_match': True, 'target_exists': True},
         {'is_new': False}),  # setting=True, usernames match
        ({'setting': False, 'user_provided': True, 'username_match': True, 'target_exists': True},
         {'is_new': False}),  # setting=False, usernames match
        ({'setting': True, 'user_provided': True, 'username_match': False, 'target_exists': True},
         {'is_new': False, 'user': 'target_user'}),  # setting=True, mismatch with target
        ({'setting': False, 'user_provided': True, 'username_match': False, 'target_exists': True},
         {'is_new': False}),  # setting=False, mismatch with target
        ({'setting': True, 'user_provided': True, 'username_match': False, 'target_exists': False},
         {}),  # setting=True, mismatch no target
    )
    @ddt.unpack
    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_user_scenarios(self, test_config, expected_result, mock_set_attribute, mock_logger):
        """
        Test various user scenarios with different settings and user conditions.
        """
        setting_value = test_config['setting']
        user_provided = test_config['user_provided']
        username_match = test_config['username_match']
        target_exists = test_config['target_exists']

        with override_settings(IGNORE_LOGGED_IN_USER_ON_MISMATCH=setting_value):
            if user_provided:
                user = User.objects.create(username='existing_user')
                if username_match:
                    details = {'username': 'existing_user'}
                else:
                    if target_exists:
                        target_user = User.objects.create(username='different_user')
                        details = {'username': 'different_user'}

                        if expected_result.get('user') == 'target_user':
                            expected_result['user'] = target_user
                    else:
                        details = {'username': 'nonexistent_user'}
            else:
                user = None
                found_user = User.objects.create(username=self.username)
                details = self.details

                if expected_result.get('user') == 'found_user':
                    expected_result['user'] = found_user

            actual = get_user_if_exists(None, details, user=user)
            self.assertDictEqual(actual, expected_result)

            mock_set_attribute.assert_any_call('get_user_if_exists.ignore_toggle_enabled', setting_value)

            if user_provided:
                mock_set_attribute.assert_any_call('get_user_if_exists.username_mismatch', not username_match)

            if user_provided and not username_match and setting_value:
                mock_logger.info.assert_called_once()
                if not target_exists:
                    mock_logger.info.assert_called_with(
                        "Username mismatch detected. Username from Details: %s, Username from User: %s.",
                        'nonexistent_user',
                        'existing_user'
                    )
            else:
                mock_logger.info.assert_not_called()


class UpdateEmailPipelineTests(TestCase):
    """
    Tests for the update_email pipeline function.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='test_user')
        self.strategy = load_strategy()

    @patch('auth_backends.pipeline.SKIP_UPDATE_EMAIL_ON_USERNAME_MISMATCH.is_enabled')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email(self, mock_set_attribute, mock_toggle):
        """
        Verify that user email is updated upon changing email when usernames match.
        """
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
        """
        Verify that user email is not updated if email value is None.
        """
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
        """
        Verify that email is not updated when usernames don't match and toggle is enabled.
        """
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
        """
        Verify that email is updated when usernames don't match but toggle is disabled.
        """
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
        """
        Assert that a specific attribute was or was not set via set_custom_attribute.
        """
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
