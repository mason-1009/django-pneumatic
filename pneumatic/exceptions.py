from typing import Literal


TaskType = Literal["InboxItem", "OutboxItem"]


class InvalidTaskName(Exception):
    """
    Thrown when an inbox or outbox message is scheduled for a task name without
    a registered handler.
    """

    def __init__(self, task_type: TaskType, task_name: str) -> None:
        super().__init__(f"Invalid task name {task_name} for {task_type}")

        self._task_type = task_type
        self._task_name = task_name

    @property
    def task_type(self) -> TaskType:
        return self._task_type

    @property
    def task_name(self) -> str:
        return self._task_name


class InvalidStateTransition(Exception):
    """
    Thrown when a state transition is invalid and cannot be completed.
    """

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid state: cannot transitionfrom {from_state} to {to_state}"
        )

        self._from_state = from_state
        self._to_state = to_state

    @property
    def from_state(self) -> str:
        return self._from_state

    @property
    def to_state(self) -> str:
        return self._to_state
