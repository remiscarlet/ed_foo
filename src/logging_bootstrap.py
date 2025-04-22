import logging
from typing import Any

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


class TraceLogger(logging.Logger):
    def trace(self, msg: str, *args: Any, **kws: Any) -> None:
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, msg, args, **kws)


logging.setLoggerClass(TraceLogger)
