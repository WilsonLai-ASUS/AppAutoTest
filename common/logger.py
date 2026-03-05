# logger.py

"""
Logger utility for logging messages during tests.
"""

import inspect
import os
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    FAIL = (0, "FAIL")
    PASS = (1, "PASS")
    ERROR = (2, "ERROR")
    WARN = (3, "WARN")
    INFO = (4, "INFO")
    DEBUG = (5, "DEBUG")


class Colors:
    """ANSI Color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class Logger:
    path = None
    level = LogLevel.DEBUG

    def __init__(self):
        pass

    def set_path(self, path):
        self.path = path

    def set_level(self, level):
        if isinstance(level, LogLevel):
            self.level = level
        elif isinstance(level, int):
            for log_level in LogLevel:
                if log_level.value[0] == level:
                    self.level = log_level
                    break
        elif isinstance(level, str):
            for log_level in LogLevel:
                if log_level.value[1].upper() == level.upper():
                    self.level = log_level
                    break

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _caller_filename(self) -> str:
        try:
            frame = inspect.currentframe()
            # self._caller_filename -> log -> (info/debug/...) -> caller
            while frame is not None:
                frame = frame.f_back
                if frame is None:
                    break

                filename = frame.f_code.co_filename or ""
                if filename.endswith(os.path.join("common", "logger.py")):
                    continue
                base = os.path.basename(filename)
                return base
        except Exception:
            return ""
        return ""

    def _format(self, caller: str, width: int = 32) -> str:
        caller = caller or ""
        if width <= 0:
            return ""

        # If longer than width, keep the tail (drop the head)
        caller_fixed = caller[-width:]
        return caller_fixed.ljust(width)

    def log(self, level, message, *args):
        if level.value[0] > self.level.value[0]:
            return
        if args:
            message = message % args

        timestamp = self._timestamp()
        level_format = self._format(level.value[1], width=5)
        caller_format = self._format(self._caller_filename(), width=16)

        if level == LogLevel.PASS:
            log_message = f"[{timestamp}] [{Colors.GREEN}{Colors.BOLD}{level_format}{Colors.RESET}] [{caller_format}] {message}"
        elif level == LogLevel.FAIL:
            log_message = f"[{timestamp}] [{Colors.RED}{Colors.BOLD}{level_format}{Colors.RESET}] [{caller_format}] {message}"
        else:
            log_message = f"[{timestamp}] [{level_format}] [{caller_format}] {message}"

        print(log_message)
        if self.path:
            with open(self.path, "a") as f:
                f.write(log_message + "\n")

    def error(self, message, *args):
        self.log(LogLevel.ERROR, message, *args)

    def warn(self, message, *args):
        self.log(LogLevel.WARN, message, *args)

    def passed(self, message, *args):
        self.log(LogLevel.PASS, message, *args)

    def fail(self, message, *args):
        self.log(LogLevel.FAIL, message, *args)

    def info(self, message, *args):
        self.log(LogLevel.INFO, message, *args)

    def debug(self, message, *args):
        self.log(LogLevel.DEBUG, message, *args)


# Singleton
logger = Logger()
