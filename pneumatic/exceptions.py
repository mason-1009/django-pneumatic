from typing import Literal


TaskType = Literal["InboxItem", "OutboxItem"]


class InvalidTaskConfig(Exception):
    """
    Exception thrown when a task configuration is invalid or incorrect.
    """

    ...


class InvalidTaskName(Exception):
    """
    Thrown when an inbox or outbox message is scheduled for a task name without
    a registered handler.
    """

    def __init__(self, task_type: TaskType, task_name: str) -> None:
        super().__init__(f"Invalid task name {task_name} for {task_type}")

        self.task_type = task_type
        self.task_name = task_name


class InvalidStateTransition(Exception):
    """
    Thrown when a state transition is invalid and cannot be completed.
    """

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid state: cannot transition from {from_state} to {to_state}"
        )

        self.from_state = from_state
        self.to_state = to_state
