from django.test import (
    TestCase,
    override_settings,
)

from pneumatic.config import (
    ItemConfig,
    PneumaticConfig,
    PneumaticConfigContainer,
)
from pneumatic.exceptions import InvalidTaskConfig


CUSTOM_SETTINGS = {
    'PNEUMATIC_INBOX_MAX_RETRIES': 10,
    'PNEUMATIC_INBOX_RETRYABLE_EXCEPTIONS': [ValueError],
    'PNEUMATIC_OUTBOX_MAX_RETRIES': 15,
    'PNEUMATIC_OUTBOX_RETRYABLE_EXCEPTIONS': [RuntimeError],
}


class ItemConfigTestCase(TestCase):
    def test_exception_is_retryable(self):
        for exc, exceptions, result in [
            (Exception('test'), [], False),
            (Exception('test'), [BaseException], True),
            (Exception('test'), [Exception, BaseException], True),
            (ValueError('test'), [], False),
            (ValueError('test'), [BaseException], True),
            (ValueError('test'), [Exception, BaseException], True),
            (BaseException('test'), [Exception], False),
            (Exception('test'), [ValueError], False),
        ]:
            with self.subTest(exc=exc.__class__.__name__, result=result):
                config = ItemConfig(
                    max_retries=3, retryable_exceptions=exceptions
                )
                self.assertEqual(
                    config.exception_is_retryable(exc=exc), result
                )


class PneumaticConfigTestCase(TestCase):
    def test_default_settings(self):
        config = PneumaticConfig.from_django_settings()

        self.assertEqual(config.inbox_config.max_retries, 3)
        self.assertEqual(config.outbox_config.max_retries, 3)

        self.assertCountEqual(config.inbox_config.retryable_exceptions, [])
        self.assertCountEqual(config.outbox_config.retryable_exceptions, [])

    @override_settings(**CUSTOM_SETTINGS)
    def test_custom_settings(self):
        config = PneumaticConfig.from_django_settings()

        self.assertEqual(config.inbox_config.max_retries, 10)
        self.assertEqual(config.outbox_config.max_retries, 15)

        self.assertCountEqual(
            config.inbox_config.retryable_exceptions, [ValueError]
        )
        self.assertCountEqual(
            config.outbox_config.retryable_exceptions, [RuntimeError]
        )

    @override_settings(PNEUMATIC_INBOX_RETRYABLE_EXCEPTIONS=1)
    def test_invalid_setting_throws_exception(self):
        with self.assertRaises(InvalidTaskConfig):
            PneumaticConfig.from_django_settings()


class PneumaticConfigContainerTestCase(TestCase):
    def test_get_config_empty(self):
        PneumaticConfigContainer.pneumatic_config = None
        config = PneumaticConfigContainer.get_config()

        self.assertIsNotNone(config)
        self.assertIs(config, PneumaticConfigContainer.pneumatic_config)
