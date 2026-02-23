from uuid import UUID
from contextlib import contextmanager
from logging import getLogger as get_logger

from django.db import transaction

from pneumatic.models import (
    InboxItem,
    OutboxItem,
)

from typing import Generator, Any


Payload = dict[str, Any]
PayloadGenerator = Generator[Payload, None, None]

logger = get_logger(__name__)

# TODO: Pull this from a configuration value/policy
MAX_FAILURES: int = 3


@contextmanager
def _handle_atomically(item: InboxItem | OutboxItem) -> PayloadGenerator:
    with transaction.atomic():
        item.transition_started()

        try:
            yield item.payload
        except Exception:
            item.record_failure(max_failures=MAX_FAILURES)
        else:
            item.transition_completed()


@contextmanager
def handle_inbox(inbox_item_uuid: str | UUID) -> PayloadGenerator:
    inbox_item = InboxItem.objects.get(uuid=inbox_item_uuid)  # type: ignore

    with _handle_atomically(item=inbox_item) as payload:
        yield payload


@contextmanager
def handle_outbox(outbox_item_uuid: str | UUID) -> PayloadGenerator:
    outbox_item = OutboxItem.objects.get(uuid=outbox_item_uuid)  # type: ignore

    with _handle_atomically(item=outbox_item) as payload:
        yield payload
