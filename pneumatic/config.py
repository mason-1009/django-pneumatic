from dataclasses import (
    dataclass,
)
from django.conf import settings


from typing import Self


DEFAULT_MAX_RETRIES: int = 3


@dataclass
class ItemConfig:
    """
    Represents configuration for a single item (both inbox or outbox)
    for configuration spec reuse.

    Fields:
        - `max_retries`: Indicates the maximum number of retries before an item
          is marked as a permanent failure (default: 3 retries).

        - `retryable_exceptions`: A list of exception classes that
          should result in retry attempts. If empty, all exceptions are
          treated as immediate failures.
    """

    max_retries: int
    retryable_exceptions: set[type[BaseException]]

    def exception_is_retryable(self, exc: BaseException) -> bool:
        """
        Returns a boolean indicating whether a given exception is considered
        retryable according to the configuration.
        """

        # Use method resolution order to handle subclasses
        for klass in exc.__class__.mro():
            if klass in self.retryable_exceptions:
                return True

        return False


@dataclass
class PneumaticConfig:
    """
    Configuration class for inbox and outbox task scheduling,
    management, and error handling.
    """

    inbox_config: ItemConfig
    outbox_config: ItemConfig

    @classmethod
    def from_django_settings(cls) -> Self:
        """
        Produces an instance of the config from available
        `django.conf.settings` values, using default values if none are
        specified.
        """

        # TODO: Throw a custom exception for invalid configuration values/types
        # in application settings
        return cls(
            inbox_config=ItemConfig(
                max_retries=getattr(
                    settings, "PNEUMATIC_INBOX_MAX_RETRIES", DEFAULT_MAX_RETRIES
                ),
                retryable_exceptions=set(
                    getattr(settings, "PNEUMATIC_INBOX_RETRYABLE_EXCEPTIONS", [])
                ),
            ),
            outbox_config=ItemConfig(
                max_retries=getattr(
                    settings, "PNEUMATIC_OUTBOX_MAX_RETRIES", DEFAULT_MAX_RETRIES
                ),
                retryable_exceptions=set(
                    getattr(settings, "PNEUMATIC_OUTBOX_RETRYABLE_EXCEPTIONS", [])
                ),
            ),
        )


class PneumaticConfigContainer:
    pneumatic_config: PneumaticConfig | None = None

    @classmethod
    def get_config(cls) -> PneumaticConfig:
        if cls.pneumatic_config is None:
            cls.pneumatic_config = PneumaticConfig.from_django_settings()
        return cls.pneumatic_config
