from logging import getLogger as get_logger

from pneumatic.registry import Registry
from pneumatic.models import (
    ItemStatus,
    InboxItem,
    OutboxItem,
)
from pneumatic.exceptions import (
    InvalidTaskName,
)

from typing import Any


logger = get_logger(__name__)

# TODO: Pull this from a settings policy/config
DEFAULT_BATCH_SIZE: int = 10


def schedule_inbox(task_name: str, payload: dict[str, Any]) -> str:
    """
    Creates an inbox task in a scheduled status to be executed asynchronously
    later. Accepts the name of the task and the payload contents. Returns the
    created item UUID as a string.
    """

    if not Registry.has_inbox_key(task_name=task_name):
        raise InvalidTaskName(task_type="InboxItem", task_name=task_name)

    item = (
        InboxItem.objects.create(task_name=task_name, payload=payload)  # type: ignore
    )
    return str(item.uuid)


def run_inbox_tasks(batch_size: int = DEFAULT_BATCH_SIZE) -> None:
    """
    Executes decorated handlers to trigger inbox tasks. Given the asynchronous
    nature of inbox tasks, this method should invoke methods which schedule
    asynchronous execution of inbox tasks in another method (using Celery for
    example).

    Arguments:
        batch_size: Number of inbox tasks to schedule at a time
    """

    inbox_items = InboxItem.objects.filter(status=ItemStatus.SCHEDULED)[0:batch_size]  # type: ignore

    for inbox_item in inbox_items:
        task_name = inbox_item.task_name
        method = Registry.get_inbox(task_name=task_name)

        logger.info(f"Invoking inbox method for {task_name}")
        method(str(inbox_item.uuid), inbox_item.payload)


def schedule_outbox(task_name: str, payload: dict[str, Any]) -> str:
    """
    Creates an outbox task in a scheduled status to be executed asynchronously
    later. Accepts the name of the task and the payload contents. Returns the
    create item UUID as a string.
    """

    if not Registry.has_outbox_key(task_name=task_name):
        raise InvalidTaskName(task_type="OutboxItem", task_name=task_name)

    item = (
        OutboxItem.objects.create(task_name=task_name, payload=payload)  # type: ignore
    )
    return str(item.uuid)


def run_outbox_tasks(batch_size: int = DEFAULT_BATCH_SIZE) -> None:
    """
    Executes decorated handlers to trigger outbox tasks. Given the asynchronous
    nature of outbox tasks, this method should invoke methods which schedule
    asynchronous execution of outbox tasks in another method (using Celery for
    example).

    Arguments:
        batch_size: Number of outbox tasks to schedule at a time
    """

    outbox_items = OutboxItem.objects.filter(status=ItemStatus.SCHEDULED)[0:batch_size]  # type: ignore

    for outbox_item in outbox_items:
        task_name = outbox_item.task_name
        method = Registry.get_outbox(task_name=task_name)

        logger.info(f"Invoking outbox method for {task_name}")
        method(str(outbox_item.uuid), outbox_item.payload)
