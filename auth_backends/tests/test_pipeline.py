from django.contrib.auth import get_user_model
from django.test import TestCase
from django_dynamic_fixture import G

from auth_backends.pipeline import get_user_if_exists


class PipelineTests(TestCase):
    def setUp(self):
        self.user = get_user_model()

    def test_get_user_if_exists(self):
        username = 'edx'
        details = {'username': username}

        # If no user exists, return an empty dict
        actual = get_user_if_exists(None, details)
        self.assertDictEqual(actual, {})

        # If user exists, return dict with user and any additional information
        user = G(self.user, username=username)
        actual = get_user_if_exists(None, details)
        self.assertDictEqual(actual, {'is_new': False, 'user': user})

        # If user passed to function, just return the additional information
        actual = get_user_if_exists(None, details, user=user)
        self.assertDictEqual(actual, {'is_new': False})
