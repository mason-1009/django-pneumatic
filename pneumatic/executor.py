from uuid import UUID
from contextlib import contextmanager
from logging import getLogger as get_logger

from django.db import transaction

from pneumatic.models import (
    InboxItem,
    OutboxItem,
)
from pneumatic.config import (
    ItemConfig,
    PneumaticConfigContainer,
)

from typing import Generator, Any


Payload = dict[str, Any]
PayloadGenerator = Generator[Payload, None, None]

logger = get_logger(__name__)


@contextmanager
def _handle_atomically(
    item: InboxItem | OutboxItem, item_config: ItemConfig
) -> PayloadGenerator:
    with transaction.atomic():
        item.transition_started()

        try:
            yield item.payload
        except Exception as exc:
            if item_config.exception_is_retryable(exc=exc):
                item.record_failure(max_failures=item_config.max_retries)
            else:
                # Exceptions that are non-retryable are directly transitioned
                # to failure
                item.transition_failed()
        else:
            item.transition_completed()


@contextmanager
def handle_inbox(inbox_item_uuid: str | UUID) -> PayloadGenerator:
    inbox_item = InboxItem.objects.get(uuid=inbox_item_uuid)  # type: ignore

    config = PneumaticConfigContainer.get_config().inbox_config
    with _handle_atomically(item=inbox_item, item_config=config) as payload:
        yield payload


@contextmanager
def handle_outbox(outbox_item_uuid: str | UUID) -> PayloadGenerator:
    outbox_item = OutboxItem.objects.get(uuid=outbox_item_uuid)  # type: ignore

    config = PneumaticConfigContainer.get_config().outbox_config
    with _handle_atomically(item=outbox_item, item_config=config) as payload:
        yield payload
