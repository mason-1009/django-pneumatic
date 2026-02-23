from django.test import TestCase

from pneumatic.models import (
    ItemStatus,
    InboxItem,
    OutboxItem,
)
from pneumatic.scheduler import (
    schedule_inbox,
    schedule_outbox,
)
from pneumatic.exceptions import (
    InvalidTaskName,
)
from pneumatic.registry import Registry

from typing import Any


class SchedulerTestCase(TestCase):
    def setUp(self):
        super().setUp()

        # Clear before each test
        Registry.reset()

    def test_schedule_inbox_success(self):
        def _schedule(uuid: str, payload: dict[str, Any]) -> None:
            ...

        Registry.register_inbox(
            task_name='inbox.test', handler=_schedule
        )
        item_uuid = schedule_inbox(
            task_name='inbox.test', payload={'key': 'value'}
        )

        item = InboxItem.objects.get(uuid=item_uuid)

        self.assertEqual(item.task_name, 'inbox.test')
        self.assertDictEqual(item.payload, {'key': 'value'})

    def test_schedule_inbox_unregistered(self):
        with self.assertRaises(InvalidTaskName):
            schedule_inbox(
                task_name='inbox.test', payload={'key': 'value'}
            )

    def test_schedule_outbox_success(self):
        def _schedule(uuid: str, payload: dict[str, Any]) -> None:
            ...

        Registry.register_outbox(
            task_name='outbox.test', handler=_schedule
        )
        item_uuid = schedule_outbox(
            task_name='outbox.test', payload={'key': 'value'}
        )

        item = OutboxItem.objects.get(uuid=item_uuid)

        self.assertEqual(item.task_name, 'outbox.test')
        self.assertDictEqual(item.payload, {'key': 'value'})

    def test_schedule_outbox_unregistered(self):
        with self.assertRaises(InvalidTaskName):
            schedule_outbox(
                task_name='outbox.test', payload={'key': 'value'}
            )
