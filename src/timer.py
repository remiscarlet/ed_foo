import inspect
import time
from typing import Optional


class Timer:
    def __init__(self, name: Optional[str] = None, debug = True):
        self.__debug = debug
        self.__start = time.time()
        if name:
            self.__name = name
        else:
            self.__name = inspect.stack()[1].function

    def restart(self):
        self.__start = time.time()

    def end(self, return_time=False):
        dur = time.time() - self.__start

        if return_time:
            return dur
        elif self.__debug:
            print(f"[{self.__name}] Took {dur:.2f} seconds")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
