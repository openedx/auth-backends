""" Tests for pipelines. """

from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase

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
        self.strategy = MagicMock()

        # Make strategy.storage.user.changed actually save the user
        def save_user(user):
            user.save()

        self.strategy.storage.user.changed.side_effect = save_user

    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email(self, mock_set_attribute):
        """ Verify that user email is updated upon changing email when usernames match. """
        updated_email = 'updated@example.com'
        self.assertNotEqual(self.user.email, updated_email)

        # Provide matching username in details
        update_email(self.strategy, {'email': updated_email, 'username': 'test_user'}, user=self.user)

        # Verify email was updated
        self.user = User.objects.get(username=self.user.username)
        self.assertEqual(self.user.email, updated_email)
        self.strategy.storage.user.changed.assert_called_once_with(self.user)

        # Verify custom attribute was set correctly
        mock_set_attribute.assert_called_with('update_email.username_mismatch', False)

    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_update_email_with_none(self, mock_set_attribute):
        """ Verify that user email is not updated if email value is None. """
        old_email = self.user.email

        # Provide matching username in details
        update_email(self.strategy, {'email': None, 'username': 'test_user'}, user=self.user)

        # Verify email was not updated
        self.user = User.objects.get(username=self.user.username)
        self.assertEqual(self.user.email, old_email)
        self.strategy.storage.user.changed.assert_not_called()

        # Verify custom attribute was still set
        mock_set_attribute.assert_called_with('update_email.username_mismatch', False)

    @patch('auth_backends.pipeline.logger')
    @patch('auth_backends.pipeline.set_custom_attribute')
    def test_username_mismatch_no_update(self, mock_set_attribute, mock_logger):
        """ Verify that email is not updated when usernames don't match. """
        old_email = self.user.email
        updated_email = 'updated@example.com'

        # Provide mismatched username in details
        update_email(self.strategy, {'email': updated_email, 'username': 'different_user'}, user=self.user)

        # Verify email was not updated
        self.user = User.objects.get(username=self.user.username)
        self.assertEqual(self.user.email, old_email)
        self.strategy.storage.user.changed.assert_not_called()

        # Verify logger was called with warning
        mock_logger.warning.assert_called_once()

        # Verify all custom attributes were set correctly
        mock_set_attribute.assert_any_call('update_email.username_mismatch', True)
        mock_set_attribute.assert_any_call('update_email.details_username', 'different_user')
        mock_set_attribute.assert_any_call('update_email.user_username', 'test_user')
