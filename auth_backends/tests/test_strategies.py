""" Tests for the strategies. """
from django.conf import settings
from django.test import TestCase
from django.test import override_settings
from social_django.utils import load_strategy

from auth_backends.strategies import EdxDjangoStrategy


class EdxDjangoStrategyTests(TestCase):
    """ Tests for the EdxDjangoStrategy Python Social Auth strategy. """

    def setUp(self):
        super(EdxDjangoStrategyTests, self).setUp()
        self.strategy = load_strategy()

    def test_load_strategy(self):
        """ Verify the correct strategy has been loaded.

        Note:
            The strategy should be set in test settings.
        """
        self.assertIsInstance(self.strategy, EdxDjangoStrategy)

    def test_get_setting(self):
        """ Verify the method returns settings defined in Django settings, or defaults from the strategy. """
        setting_name = 'SOCIAL_AUTH_USER_FIELDS'

        # This should pull the value from the defaults declared in settings.
        expected = ['username', 'email', 'first_name', 'last_name']
        self.assertEqual(self.strategy.get_setting(setting_name), expected)

        # This should pull the value as defined/overridden in Django settings
        expected = None
        with override_settings(**{setting_name: expected}):
            self.assertEqual(getattr(settings, setting_name), expected)
            self.assertEqual(self.strategy.get_setting(setting_name), expected)
