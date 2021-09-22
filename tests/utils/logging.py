from typing import Dict, List

import logging


class SelfLogger(logging.Logger):
    """
    A logger for testing that appends its messages to a dict instance variable
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logged_messages: Dict[int, List[str]] = {}

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, args, **kwargs)

    def _log(self, level, msg, *args, **kwargs):
        if level not in self.logged_messages:
            self.logged_messages[level] = [msg]
        else:
            self.logged_messages[level].append(msg)
