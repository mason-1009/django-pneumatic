from logging import getLogger as get_logger

from pneumatic.types import HandlerMethod
from pneumatic.registry import Registry


logger = get_logger(__name__)


def _get_callable_name(func: HandlerMethod) -> str:
    if (name := getattr(func, "__name__", None)) is not None:
        return name
    raise ValueError("Passed callable does not have __name__")


def inbox_handler(func: HandlerMethod):
    name = _get_callable_name(func=func)
    logger.debug(f"Registered inbox handler {name}")
    Registry.register_inbox(task_name=name, handler=func)
    return func


def outbox_handler(func: HandlerMethod):
    name = _get_callable_name(func=func)
    logger.debug(f"Registered outbox handler {name}")
    Registry.register_outbox(task_name=name, handler=func)
    return func
