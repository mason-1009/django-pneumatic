from django.test import TestCase
from unittest import mock

from pneumatic.models import (
    ItemStatus,
    InboxItem,
    OutboxItem,
)
from pneumatic.executor import (
    handle_inbox,
    handle_outbox,
)
from pneumatic.config import (
    ItemConfig,
    PneumaticConfig,
    PneumaticConfigContainer,
)


class WithMockConfig(TestCase):
    def setUp(self):
        super().setUp()

        item_config = ItemConfig(
            max_retries=3,
            retryable_exceptions={ValueError}
        )

        self.test_config = PneumaticConfig(
            inbox_config=item_config,
            outbox_config=item_config
        )

        self.patcher = mock.patch.object(
            PneumaticConfigContainer,
            'get_config', return_value=self.test_config
        )
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()


class HandleInboxTestCase(WithMockConfig):
    def setUp(self):
        super().setUp()

        self.payload = {
            'key': 'value',
        }
        self.inbox_item = InboxItem.objects.create(
            task_name='test.task',
            payload=self.payload
        )

    def test_handle_inbox_success(self):
        with handle_inbox(inbox_item_uuid=self.inbox_item.uuid) as payload:
            self.assertDictEqual(payload, self.inbox_item.payload)

        self.inbox_item.refresh_from_db()
        self.assertEqual(self.inbox_item.status, ItemStatus.COMPLETED)

    def test_handle_inbox_one_error(self):
        with handle_inbox(inbox_item_uuid=self.inbox_item.uuid) as _:
            raise ValueError('Test exception')

        self.inbox_item.refresh_from_db()
        self.assertEqual(self.inbox_item.status, ItemStatus.SCHEDULED)
        self.assertEqual(self.inbox_item.failure_count, 1)

    def test_handle_inbox_max_errors(self):
        for _ in range(3):
            with handle_inbox(inbox_item_uuid=self.inbox_item.uuid) as _:
                raise ValueError('Test exception')

        self.inbox_item.refresh_from_db()
        self.assertEqual(self.inbox_item.status, ItemStatus.FAILED)
        self.assertEqual(self.inbox_item.failure_count, 3)

    def test_handle_inbox_non_retryable(self):
        with handle_inbox(inbox_item_uuid=self.inbox_item.uuid) as _:
            raise Exception('Immediate failure')

        self.inbox_item.refresh_from_db()
        self.assertEqual(self.inbox_item.status, ItemStatus.FAILED)
        self.assertEqual(self.inbox_item.failure_count, 0)


class HandleOutboxTestCase(WithMockConfig):
    def setUp(self):
        super().setUp()

        self.payload = {
            'key': 'value',
        }
        self.outbox_item = OutboxItem.objects.create(
            task_name='test.task',
            payload=self.payload
        )

    def test_handle_outbox_success(self):
        with handle_outbox(outbox_item_uuid=self.outbox_item.uuid) as payload:
            self.assertDictEqual(payload, self.outbox_item.payload)

        self.outbox_item.refresh_from_db()
        self.assertEqual(self.outbox_item.status, ItemStatus.COMPLETED)

    def test_handle_outbox_one_error(self):
        with handle_outbox(outbox_item_uuid=self.outbox_item.uuid) as _:
            raise ValueError('Test exception')

        self.outbox_item.refresh_from_db()
        self.assertEqual(self.outbox_item.status, ItemStatus.SCHEDULED)
        self.assertEqual(self.outbox_item.failure_count, 1)

    def test_handle_outbox_max_errors(self):
        for _ in range(3):
            with handle_outbox(outbox_item_uuid=self.outbox_item.uuid) as _:
                raise ValueError('Test exception')

        self.outbox_item.refresh_from_db()
        self.assertEqual(self.outbox_item.status, ItemStatus.FAILED)
        self.assertEqual(self.outbox_item.failure_count, 3)

    def test_handle_outbox_non_retryable(self):
        with handle_outbox(outbox_item_uuid=self.outbox_item.uuid) as _:
            raise Exception('Immediate failure')

        self.outbox_item.refresh_from_db()
        self.assertEqual(self.outbox_item.status, ItemStatus.FAILED)
        self.assertEqual(self.outbox_item.failure_count, 0)
