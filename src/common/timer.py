import inspect
import time
from types import TracebackType
from typing import Optional

from src.common.logging import get_logger
from src.common.utils import seconds_to_str

logger = get_logger(__name__)


class Timer:
    def __init__(self, name: Optional[str] = None) -> None:
        self.__start = time.time()
        if name:
            self.__name = name
        else:
            self.__name = inspect.stack()[1].function

    def running_for(self) -> float:
        return time.time() - self.__start

    def running_for_str(self) -> str:
        return seconds_to_str(time.time() - self.__start)

    last_lap = None

    def lap(self, log: bool = True) -> float:
        now = time.time()
        last_lap = self.last_lap if self.last_lap is not None else self.__start
        dur = now - last_lap
        self.last_lap = now

        if log:
            self.log(dur, True)
        return dur

    def reset(self) -> None:
        now = time.time()
        self.__start = now

    def end(self, log: bool = True) -> float:
        now = time.time()
        dur = now - self.__start
        self.__start = now

        if log:
            self.log(dur)
        return dur

    def log(self, dur: float, lap: bool = False) -> None:
        if lap:
            msg = f"[{self.__name}] Lapped in {seconds_to_str(dur)} seconds"
        else:
            msg = f"[{self.__name}] Took {seconds_to_str(dur)} seconds total"
        logger.info(msg)

    def __enter__(self) -> "Timer":
        return self

    def __exit__(
        self, type_: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self.end()
