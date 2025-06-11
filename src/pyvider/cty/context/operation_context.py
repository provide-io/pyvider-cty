# pyvider/conversion/context/operation_context.py

from contextvars import ContextVar
from enum import Enum, auto
from typing import ContextManager

from pyvider.telemetry import logger


class OperationContext(Enum):
    DEFAULT = auto()
    CONFIG = auto()
    STATE = auto()
    PLAN = auto()
    APPLY = auto()
    READ = auto()
    FUNCTION = auto()
    SCHEMA = auto()


_current_operation_context: ContextVar[OperationContext] = ContextVar(
    "current_operation_context", default=OperationContext.DEFAULT
)


def get_current_operation() -> OperationContext:
    return _current_operation_context.get()


def operation_context(context: OperationContext) -> ContextManager[None]:
    class OperationContextManager:
        def __init__(self, new_context: OperationContext) -> None:
            self._new_context = new_context
            self._token = None

        def __enter__(self) -> None:
            logger.debug(f"🧰🔄📊 Pushed operation context: {self._new_context.name}")
            self._token = _current_operation_context.set(self._new_context)

        def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
            if self._token:
                current_context_before_reset = _current_operation_context.get()
                _current_operation_context.reset(self._token)
                newly_restored_context_name = _current_operation_context.get().name
                logger.debug(
                    f"🧰🔄📊 Popped operation context: {current_context_before_reset.name} -> {newly_restored_context_name}"
                )
            self._token = None

    return OperationContextManager(context)
