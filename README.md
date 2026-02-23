# `django-pneumatic`

> The easy inbox and outbox pattern library for Django web applications.

---

## Introduction

The `django-pneumatic` library eases the implementation of the inbox and outbox
patterns in *Django* applications. The inbox pattern and the outbox pattern are
set of design patterns wherein incoming and outgoing messages are stored and
persisted in a database to ensure reliable delivery.

The `django-pneumatic` library uses atomic transactions to ensure that data
enters and exits your application reliably.

## Usage

### Register

Each inbox and outbox operation has a name (`task_name`) and a
scheduler/handler. To register a handler to a task name, use the decorator on a
method of the desired identifier. Typically, these handlers trigger an
asynchronous task (for example in Celery), rather than run the
sending/receiving code directly:

```python
from pneumatic.decorators import inbox_handler, outbox_handler
from typing import Any

@inbox_handler
def my_inbox_task(item_uuid: str, payload: dict[str, Any]) -> None:
    my_async_inbox_task.delay(item_uuid)

@outbox_handler
def my_outbox_task(item_uuid: str, payload: dict[str, Any]) -> None:
    my_async_outbox_task.delay(item_uuid)
```

### Schedule Messages

When an inbox or outbox message needs to be received or sent,
`django-pneumatic` requires it be scheduled:

```python
from pneumatic.scheduler import schedule_inbox, schedule_outbox

# `payload` is all relevant data to execute the task
schedule_inbox(task_name='my_inbox_task', payload=payload)
schedule_inbox(task_name='my_outbox_task', payload=payload)
```

This creates the message and stores it in a scheduled state.

### Sending Messages

Scheduled messages are triggered in batches:

```python
from pneumatic.scheduler import run_inbox_tasks, run_outbox_tasks

# Perform this in a periodic task or when needed
run_inbox_tasks()
run_outbox_tasks()
```

### Ensuring Delivery

`django-pneumatic` provides a context manager for ensuring delivery and
atomicity when it comes time to deliver. In the task or method that handles the
payload, use the context manager and provide it with the task identifier:

```python
from pneumatic.executor import handle_inbox, handle_outbox

@celery.shared_task
def my_async_inbox_task(item_uuid: str) -> None:
    with handle_inbox(inbox_item_uuid=item_uuid) as payload:
        # Do something with the payload
        ...

@celery.shared_task
def my_async_outbox_task(item_uuid: str) -> None:
    with handle_outbox(outbox_item_uuid=item_uuid) as payload:
        # Do something with the payload
        ...
```

Throw any exceptions and the operation will abort atomically, returning the
item to a scheduled state for a later retry. After a specified number of
retries, the item will transition to a failed state. A successful run
transitions the item to a completed state.

## How to Contribute

### Linters and Tests

Before beginning, ensure the `uv` package manager is installed and accessible
on your system (e.g. in your `$PATH` variable on *Linux* or *Mac OS*).

This project uses *GNU Make* as its primary build tool. To invoke unit tests,
run the following command:

```bash
make test
```

To run tests, linters (*Ruff*), type-checking (*Ty*), formatting (*Ruff*), and
unit tests, run the following command:

```bash
make check
```
