import inspect
import time
from types import TracebackType
from typing import Optional

from src.common.logging import get_logger

logger = get_logger(__name__)


class Timer:
    def __init__(self, name: Optional[str] = None, force_print: bool = False) -> None:
        self.__force_print = force_print
        self.__start = time.time()
        if name:
            self.__name = name
        else:
            self.__name = inspect.stack()[1].function

    def restart(self) -> None:
        self.__start = time.time()

    def end(self) -> float:
        dur = time.time() - self.__start

        if self.__force_print:
            log_fn = logger.info
        else:
            log_fn = logger.debug
        log_fn(f"[{self.__name}] Took {dur:.2f} seconds")

        return dur

    def __enter__(self) -> "Timer":
        return self

    def __exit__(
        self, type_: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self.end()
