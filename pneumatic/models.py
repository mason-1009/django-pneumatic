import uuid
from django.db import models
from django.utils.translation import gettext_lazy as gt

from pneumatic.exceptions import InvalidStateTransition


class ItemStatus(models.TextChoices):
    """
    List of valid states for an inbox or outbox item to be in.
    """

    SCHEDULED = "scheduled", gt("Scheduled")
    STARTED = "started", gt("Started")
    COMPLETED = "completed", gt("Completed")
    FAILED = "failed", gt("Failed")


class BaseItem(models.Model):
    """
    Base item to share common fields among inbox and outbox items. The
    `task_name` field refers to the type of operation it represents (example:
    `receive.webhook.example_webhook`).
    """

    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )

    created_at = models.DateTimeField(null=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    task_name = models.CharField(null=False, blank=False, max_length=256)

    payload = models.JSONField()

    status = models.CharField(
        max_length=24, null=False, choices=ItemStatus, default=ItemStatus.SCHEDULED
    )

    failure_count = models.PositiveSmallIntegerField(default=0)

    def transition_started(self) -> None:
        if not self.status == ItemStatus.SCHEDULED:
            raise InvalidStateTransition(
                from_state=str(self.status), to_state=str(ItemStatus.STARTED)
            )

        self.status = ItemStatus.STARTED
        self.save()

    def transition_completed(self) -> None:
        if not self.status == ItemStatus.STARTED:
            raise InvalidStateTransition(
                from_state=str(self.status), to_state=str(ItemStatus.COMPLETED)
            )

        self.status = ItemStatus.COMPLETED
        self.save()

    def transition_failed(self) -> None:
        if not self.status == ItemStatus.STARTED:
            raise InvalidStateTransition(
                from_state=str(self.status), to_state=str(ItemStatus.FAILED)
            )

        self.status = ItemStatus.FAILED
        self.save()

    def record_failure(self, max_failures: int) -> None:
        """
        Records a failure to perform a task, transitioning the item to a failed
        state if the number of failures have reached the `max_failures` amount.
        """

        self.failure_count += 1  # type: ignore

        if self.failure_count >= max_failures:
            self.status = ItemStatus.FAILED
        else:
            self.status = ItemStatus.SCHEDULED

        self.save()

    class Meta:
        abstract = True


class InboxItem(BaseItem):
    """
    Represents a single inbox item, which is an incoming message that is stored
    and atomically processed.
    """

    ...


class OutboxItem(BaseItem):
    """
    Represents a single outbox item, which is an outgoing message that is
    stored and atomically processed.
    """

    ...
