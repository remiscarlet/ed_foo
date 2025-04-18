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

    def end(self):
        end = time.time()
        print(f"[{self.__name}] {end - self.__start:.2f} seconds")
