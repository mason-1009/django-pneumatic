from django.test import TestCase

from pneumatic.models import (
    ItemStatus,
    InboxItem,
    OutboxItem,
)
from pneumatic.exceptions import InvalidStateTransition


class InboxItemTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.inbox_item = InboxItem.objects.create(
            task_name='example.task',
            payload={}
        )

    def test_transition_completed_success(self):
        self.inbox_item.transition_started()
        self.inbox_item.transition_completed()

        self.assertEqual(self.inbox_item.status, ItemStatus.COMPLETED)

    def test_transition_failed_success(self):
        self.inbox_item.transition_started()
        self.inbox_item.transition_failed()

        self.assertEqual(self.inbox_item.status, ItemStatus.FAILED)

    def test_transition_completed_failure(self):
        with self.assertRaises(InvalidStateTransition):
            # Cannot transition scheduled -> completed
            self.inbox_item.transition_completed()

        self.assertEqual(self.inbox_item.status, ItemStatus.SCHEDULED)

    def test_transition_failed_failure(self):
        with self.assertRaises(InvalidStateTransition):
            # Cannot transition scheduled -> failed
            self.inbox_item.transition_failed()

        self.assertEqual(self.inbox_item.status, ItemStatus.SCHEDULED)

    def test_transition_started_failure(self):
        self.inbox_item.transition_started()
        self.inbox_item.transition_completed()

        with self.assertRaises(InvalidStateTransition):
            # Cannot transition completed -> started
            self.inbox_item.transition_started()

        self.assertEqual(self.inbox_item.status, ItemStatus.COMPLETED)

    def test_record_failure_under_limit(self):
        self.inbox_item.transition_started()
        self.inbox_item.record_failure(max_failures=3)

        self.assertEqual(self.inbox_item.failure_count, 1)
        self.assertEqual(self.inbox_item.status, ItemStatus.SCHEDULED)

    def test_record_failure_at_limit(self):
        for _ in range(3):
            self.inbox_item.transition_started()
            self.inbox_item.record_failure(max_failures=3)

        self.assertEqual(self.inbox_item.failure_count, 3)
        self.assertEqual(self.inbox_item.status, ItemStatus.FAILED)


class OutboxItemTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.outbox_item = OutboxItem.objects.create(
            task_name='inbox.task',
            payload={}
        )

    def test_transition_completed_success(self):
        self.outbox_item.transition_started()
        self.outbox_item.transition_completed()

        self.assertEqual(self.outbox_item.status, ItemStatus.COMPLETED)

    def test_transition_failed_success(self):
        self.outbox_item.transition_started()
        self.outbox_item.transition_failed()

        self.assertEqual(self.outbox_item.status, ItemStatus.FAILED)

    def test_transition_completed_failure(self):
        with self.assertRaises(InvalidStateTransition):
            # Cannot transition scheduled -> completed
            self.outbox_item.transition_completed()

        self.assertEqual(self.outbox_item.status, ItemStatus.SCHEDULED)

    def test_transition_failed_failure(self):
        with self.assertRaises(InvalidStateTransition):
            # Cannot transition scheduled -> failed
            self.outbox_item.transition_failed()

        self.assertEqual(self.outbox_item.status, ItemStatus.SCHEDULED)

    def test_transition_started_failure(self):
        self.outbox_item.transition_started()
        self.outbox_item.transition_completed()

        with self.assertRaises(InvalidStateTransition):
            # Cannot transition completed -> started
            self.outbox_item.transition_started()

        self.assertEqual(self.outbox_item.status, ItemStatus.COMPLETED)

    def test_record_failure_under_limit(self):
        self.outbox_item.transition_started()
        self.outbox_item.record_failure(max_failures=3)

        self.assertEqual(self.outbox_item.failure_count, 1)
        self.assertEqual(self.outbox_item.status, ItemStatus.SCHEDULED)

    def test_record_failure_at_limit(self):

        for _ in range(3):
            self.outbox_item.transition_started()
            self.outbox_item.record_failure(max_failures=3)

        self.assertEqual(self.outbox_item.failure_count, 3)
        self.assertEqual(self.outbox_item.status, ItemStatus.FAILED)
