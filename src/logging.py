import logging
import logging.config
from argparse import Namespace

from src.constants import DEFAULT_LOG_LEVEL, LOG_DIR
from src.logging_bootstrap import TRACE_LEVEL_NUM, TraceLogger

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "TRACE",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOG_DIR / "app.log"),
            "mode": "a",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": DEFAULT_LOG_LEVEL,
        "handlers": ["console", "file"],
    },
}

# class TraceableLogger(Protocol):
#     def trace(self, msg: str, *args: Any, **kws: Any) -> None: ...
#     def debug(self, msg: str, *args: Any, **kws: Any) -> None: ...
#     def info(self, msg: str, *args: Any, **kws: Any) -> None: ...
#     def warning(self, msg: str, *args: Any, **kws: Any) -> None: ...
#     def error(self, msg: str, *args: Any, **kws: Any) -> None: ...


def get_logger(name: str) -> TraceLogger:
    return logging.getLogger(name)


def configure_logger(args: Namespace) -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    match args.verbosity:
        case 0:
            level = logging.getLevelNamesMapping().get(DEFAULT_LOG_LEVEL, logging.INFO)
        case 1:
            level = logging.DEBUG
        case _:
            level = TRACE_LEVEL_NUM

    root = logging.getLogger()
    root.setLevel(level)

    for h in root.handlers:
        h.setLevel(level)

    for name, logger in logging.root.manager.loggerDict.items():
        if not isinstance(logger, logging.Logger):
            continue
        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)
