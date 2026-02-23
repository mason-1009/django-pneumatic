from pneumatic.types import HandlerMethod


class Registry:
    """
    Application-wide singleton for registering, maintaining, and routing
    inbox and outbox events.
    """

    inbox_registry: dict[str, HandlerMethod] = {}
    outbox_registry: dict[str, HandlerMethod] = {}

    @classmethod
    def reset(cls) -> None:
        """
        Performs a hard reset of both the inbox and outbox registry, regardless
        of what is already configured.
        """

        cls.inbox_registry: dict[str, HandlerMethod] = {}
        cls.outbox_registry: dict[str, HandlerMethod] = {}

    @classmethod
    def register_inbox(cls, task_name: str, handler: HandlerMethod) -> None:
        """
        Accepts an inbox handler callable and adds it to the registry,
        initializing if needed.
        """

        cls.inbox_registry[task_name] = handler

    @classmethod
    def register_outbox(cls, task_name: str, handler: HandlerMethod) -> None:
        """
        Accepts an outbox handler callable and adds it to the registry,
        initializing if needed.
        """

        cls.outbox_registry[task_name] = handler

    @classmethod
    def has_inbox_key(cls, task_name: str) -> bool:
        """
        Returns a boolean indicating whether the specified `task_name` is
        registered as an inbox handler.
        """

        return task_name in cls.inbox_registry

    @classmethod
    def inbox_keys(cls) -> list[str]:
        """
        Returns a list of registered inbox method keys.
        """

        return list(cls.inbox_registry.keys())

    @classmethod
    def has_outbox_key(cls, task_name: str) -> bool:
        """
        Returns a boolean indicating whether the specified `task_name` is
        registered as an outbox handler.
        """

        return task_name in cls.outbox_registry

    @classmethod
    def outbox_keys(cls) -> list[str]:
        """
        Returns a list of registered outbox method keys.
        """

        return list(cls.outbox_registry.keys())

    @classmethod
    def get_inbox(cls, task_name: str) -> HandlerMethod:
        """
        Returns the inbox handler callable from the task name using the
        internal registry, throwing an exception if it does not exist.
        """

        return cls.inbox_registry[task_name]

    @classmethod
    def get_outbox(cls, task_name: str) -> HandlerMethod:
        """
        Returns the outbox handler callable from the task name using the
        internal registry, throwing an exception if it does not exist.
        """

        return cls.outbox_registry[task_name]
