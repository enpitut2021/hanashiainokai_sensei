"""Customizable logger based on loguru

dependencies can be installed with `pip install loguru`.
Run `python logger.py` to see demo output

"""

import os
import sys

from loguru import logger

class LoggerMixin:
    def __init__(self):
        """Logger mixin because loguru can't get class names
        """
        self.logger = logger.bind(classname=self.__class__.__name__)


def is_interactive():
    """True if running in a interactive environment/jupyter notebook"""
    import __main__ as main

    return not hasattr(main, "__file__")


def patcher(record):
    """Customize loguru's log format
    
    See the Loguru docs for details on `record` here, https://loguru.readthedocs.io/en/stable/api/logger.html.
    """
    if record.get("function") == "<module>":
        if is_interactive():
            record["function"] = "IPython"
        else:
            record["function"] = "Python"
            
    if record["extra"].get("classname"):
        record["extra"]["classname"] += ":"
    return record


class LevelFilter:
    def __init__(self, level):
        """Filter log records based on logging level"""
        self._level = level

    def __call__(self, record):
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        level = level.upper()
        self._level = level


def set_log_level(level):
    """Set the logging level for the logger"""
    level_filter.level = level


"""
Code that runs on `import .logger` 
"""
logger.remove()
level_filter = LevelFilter(os.environ.get("LOG_LEVEL", "INFO").upper())
config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<b>{extra[classname]}{function}:{line}</b>\t{level.icon}| {message}",
            "colorize": True,
            "filter": level_filter,
        },
    ],
    "levels": [
        d
        for d in [
            {"name": "DEBUG", "color": "white", "icon": "🐛"},
            {"name": "INFO", "color": "skyblue", "icon": "💬"},
            {"name": "SUCCESS", "color": "green", "icon": "✔️"},
            {"name": "WARNING", "color": "yellow", "icon": "⚠️"},
            {"name": "ERROR", "color": "red", "icon": "❌"},
            {"name": "CRITICAL", "color": "red", "icon": "🔥"},
        ]
    ],
    "patcher": patcher,
    "extra": {"classname": ""},
}

logger.configure(**config)

if __name__ == "__main__":
    """
    run `python logger.py` to see the output
    """

    logger.debug("Debug")
    logger.info("Info")
    logger.success("Success")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")

    print()

    set_log_level("DEBUG")
    logger.debug("Debug")
    logger.info("Info")
    logger.success("Success")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")

    print()
    
    set_log_level("Critical")
    logger.debug("Debug")
    logger.info("Info")
    logger.success("Success")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")