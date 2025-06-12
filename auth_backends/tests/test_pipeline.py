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

    def test_no_user_exists(self):
        """ Verify an empty dict is returned if no user exists. """
        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {})

    def test_existing_user(self):
        """ Verify a dict with the user and extra details is returned if the user exists. """
        user = User.objects.create(username=self.username)
        actual = get_user_if_exists(None, self.details)
        self.assertDictEqual(actual, {'is_new': False, 'user': user})

    def test_get_user_if_exists(self):
        """ Verify only the details are returned if a user is passed to the function. """
        user = User.objects.create(username=self.username)
        actual = get_user_if_exists(None, self.details, user=user)
        self.assertDictEqual(actual, {'is_new': False})


class UpdateEmailPipelineTests(TestCase):
    """ Tests for the update_email pipeline function. """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='test_user')
        self.strategy = load_strategy()

    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email(self, mock_set_attribute):
        """ Verify that user email is updated upon changing email when usernames match. """
        updated_email = 'updated@example.com'
        self.assertNotEqual(self.user.email, updated_email)

        initial_email = self.user.email

        update_email(self.strategy, {'email': updated_email, 'username': 'test_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, updated_email)
        self.assertNotEqual(updated_user.email, initial_email)

        mock_set_attribute.assert_called_with('update_email.username_mismatch', False)

    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email_with_none(self, mock_set_attribute):
        """ Verify that user email is not updated if email value is None. """
        old_email = self.user.email

        update_email(self.strategy, {'email': None, 'username': 'test_user'}, user=self.user)

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, old_email)

        mock_set_attribute.assert_called_with('update_email.username_mismatch', False)

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
        mock_set_attribute.assert_any_call('update_email.details_username', 'different_user')
        mock_set_attribute.assert_any_call('update_email.user_username', 'test_user')
        mock_set_attribute.assert_any_call('update_email.details_has_email', True)

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
        mock_set_attribute.assert_any_call('update_email.details_username', 'different_user')
        mock_set_attribute.assert_any_call('update_email.user_username', 'test_user')
        mock_set_attribute.assert_any_call('update_email.details_has_email', True)
