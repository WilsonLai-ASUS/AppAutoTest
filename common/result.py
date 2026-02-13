# error.py

"""
Error code
"""

from enum import Enum


class ResultCode(Enum):
    SUCCESS = 0

    # general errors
    FAILURE = 1
    INSTALL_FAILED = 2
    LAUNCH_FAILED = 3

    # element errors
    ELEMENT_NOT_FOUND = 10
    ELEMENT_NOT_TAPPABLE = 11
    ELEMENT_NOT_TYPABLE = 13


class Result(Exception):

    code: ResultCode = ResultCode.SUCCESS
    message: str = ""

    def __init__(self, code: ResultCode, message: str = ""):
        self.code = code
        self.message = message

    def is_success(self) -> bool:
        return self.code == ResultCode.SUCCESS

    def is_failure(self) -> bool:
        return self.code != ResultCode.SUCCESS

    def description(self) -> str:
        return f"Result({self.code}, '{self.message}')"
