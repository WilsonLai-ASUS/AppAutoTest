# logger.py

"""
Logger utility for logging messages during tests.
"""

from datetime import datetime
from email.mime import message
from enum import Enum
import inspect


class LogLevel(Enum):
    FAILED = (0, "FAILED")
    PASSED = (1, "PASSED")
    ERROR = (2, "ERROR")
    WARNING = (3, "WARNING")
    INFO = (4, "INFO")
    DEBUG = (5, "DEBUG")


class Colors:
    """ANSI 颜色代码"""

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

    def timestamp(self):
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def log(self, level, message, *args):
        if level.value[0] > self.level.value[0]:
            return
        if args:
            message = message % args

        # log_message = f"{self.timestamp()} [{level.value[1]}] {message}"

        log_message = ""

        if level == LogLevel.PASSED:
            log_message = f"{self.timestamp()} [{Colors.GREEN}{Colors.BOLD}{level.value[1]}{Colors.RESET}] {message}"
        elif level == LogLevel.FAILED:
            log_message = f"{self.timestamp()} [{Colors.RED}{Colors.BOLD}{level.value[1]}{Colors.RESET}] {message}"
        else:
            log_message = f"{self.timestamp()} [{level.value[1]}] {message}"

        print(log_message)
        if self.path:
            with open(self.path, "a") as f:
                f.write(log_message + "\n")

    def error(self, message, *args):
        self.log(LogLevel.ERROR, message, *args)

    def warning(self, message, *args):
        self.log(LogLevel.WARNING, message, *args)

    def passed(self, message, *args):
        self.log(LogLevel.PASSED, message, *args)

    def failed(self, message, *args):
        self.log(LogLevel.FAILED, message, *args)

    def info(self, message, *args):
        self.log(LogLevel.INFO, message, *args)

    def debug(self, message, *args):
        self.log(LogLevel.DEBUG, message, *args)


# Singleton
logger = Logger()
