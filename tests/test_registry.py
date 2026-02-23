from unittest import mock
from django.test import TestCase

from pneumatic.registry import Registry

from typing import Any


class RegistryTestCase(TestCase):
    def setUp(self):

        Registry.reset()

    def test_inbox(self):
        def _inbox_handler(a: str, b: dict[str, Any]) -> None:
            ...

        Registry.register_inbox(
            task_name='example_inbox', handler=_inbox_handler
        )

        self.assertTrue(Registry.has_inbox_key(task_name='example_inbox'))
        self.assertCountEqual(Registry.inbox_keys(), ['example_inbox'])
        self.assertIs(
            Registry.get_inbox(task_name='example_inbox'), _inbox_handler
        )

    def test_outbox(self):
        def _outbox_handler(a: str, b: dict[str, Any]) -> None:
            ...

        Registry.register_outbox(
            task_name='example_outbox', handler=_outbox_handler
        )

        self.assertTrue(Registry.has_outbox_key(task_name='example_outbox'))
        self.assertCountEqual(Registry.outbox_keys(), ['example_outbox'])
        self.assertIs(
            Registry.get_outbox(task_name='example_outbox'), _outbox_handler
        )
