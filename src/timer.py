import inspect
import time
from typing import Optional


class Timer:
    def __init__(self, name: Optional[str] = None):
        self.__start = time.time()
        if name:
            self.__name = name
        else:
            self.__name = inspect.stack()[1].function

        # print(f"[Timer] Starting timer for '{self.__name}'")

    def restart(self):
        self.__start = time.time()
        # print(f"[Timer] Restarting timer for '{self.__name}'")

    def end(self, return_time=False):
        dur = time.time() - self.__start

        if return_time:
            return dur
        else:
            print(f"[{self.__name}] Took {dur:.2f} seconds")
