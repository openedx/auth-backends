""" Tests for pipelines. """

from django.contrib.auth import get_user_model
from django.test import TestCase
from social_django.utils import load_strategy

from auth_backends.pipeline import get_user_if_exists, update_email

User = get_user_model()


class GetUserIfExistsPipelineTests(TestCase):
    """ Tests for the get_user_if_exists pipeline function. """

    def setUp(self):
        super(GetUserIfExistsPipelineTests, self).setUp()
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
        super(UpdateEmailPipelineTests, self).setUp()
        self.user = User.objects.create()

    def test_update_email(self):
        """ Verify that user email is updated upon changing email. """
        updated_email = 'updated@example.com'
        self.assertNotEqual(self.user.email, updated_email)

        update_email(load_strategy(), {'email': updated_email}, user=self.user)
        self.user = User.objects.get(username=self.user.username)
        self.assertEqual(self.user.email, updated_email)

    def test_update_email_with_none(self):
        """ Verify that user email is not updated if email value is None. """
        old_email = self.user.email
        update_email(load_strategy(), {'email': None}, user=self.user)
        self.user = User.objects.get(username=self.user.username)
        self.assertEqual(self.user.email, old_email)
