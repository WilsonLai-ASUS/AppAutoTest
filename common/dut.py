# app.py

"""
Configuration utilities for Appium tests.
"""

import json
import os

from .utils import Utils


class Dut:
    data = {}

    def __init__(self, path=None):
        if path is not None:
            self.load(path)

    def load(self, path):
        if not path:
            raise ValueError("Dut config path is required")

        filepath = Utils.get_absolute_path(path)
        with open(filepath, "r") as f:
            self.data = json.load(f)

        if not isinstance(self.data, dict):
            raise ValueError("Invalid dut config file: must be a JSON object")

    def ip(self):
        return self.data.get("ip", None)

    def model_name(self):
        return self.data.get("model_name", None)

    def default_local_username(self):
        return self.data.get("default_local_username", None)

    def default_local_password(self):
        return self.data.get("default_local_password", None)

    def default_wifi_ssid(self):
        return self.data.get("default_wifi_ssid", None)

    def default_wifi_password(self):
        return self.data.get("default_wifi_password", None)

    def local_username(self):
        return self.data.get("local_username", None)

    def local_password(self):
        return self.data.get("local_password", None)

    def wifi_ssid(self):
        return self.data.get("wifi_ssid", None)

    def wifi_password(self):
        return self.data.get("wifi_password", None)

    # feature support
    def is_support_default_password(self):
        return self.data.get("is_support_default_password", False)


dut = Dut()
