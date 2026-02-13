# app.py

"""
Configuration utilities for Appium tests.
"""

import json
import os

from .utils import Utils


class Dut:
    ip = ""
    username = ""
    password = ""

    def __init__(self, path=None):
        if path is not None:
            self.load(path)

    def load(self, path):
        if not path:
            raise ValueError("Dut config path is required")

        filepath = Utils.get_absolute_path(path)
        with open(filepath, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid dut config file: must be a JSON object")

        # dut
        self.ip = data.get("ip", None)
        self.username = data.get("username", None)
        self.password = data.get("password", None)


dut = Dut()
