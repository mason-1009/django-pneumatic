from datetime import time
from dataclasses import dataclass

from pneumatic.exceptions import InvalidTaskConfig


DEFAULT_BATCH_SIZE: int = 3


@dataclass
class TaskConfig:
    """
    Configuration object for an inbox or outbox task.
    """

    # Processing parameters
    batch_size: int = DEFAULT_BATCH_SIZE

    # Scheduling time
    process_after: time | None = None
    process_before: time | None = None

    def validate(self) -> None:
        """
        Validates the configuration values, throwing an `InvalidTaskConfig`
        exception if any values are invalid.
        """

        invalid_fields: set[str] = set()

        if self.batch_size <= 0:
            invalid_fields.add('batch_size')

        # Ensure times are valid
        if self.process_after is not None and self.process_before is not None:
            if self.process_before < self.process_after:
                invalid_fields.add('process_after')
                invalid_fields.add('process_before')

        if len(invalid_fields) > 0:
            raise InvalidTaskConfig(invalid_fields=list(invalid_fields))
