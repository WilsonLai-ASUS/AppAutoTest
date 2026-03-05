# app.py

"""
Configuration utilities for Appium tests.
"""

import json
import os

from .utils import Utils


class App:
    data = {}

    def __init__(self, path=None):
        if path is not None:
            self.load(path)

    # load
    def load(self, path):
        if not path:
            raise ValueError("App config path is required")

        filepath = Utils.get_absolute_path(path)
        with open(filepath, "r") as f:
            self.data = json.load(f)

        if not isinstance(self.data, dict):
            raise ValueError("Invalid app config file: must be a JSON object")

    # debug
    def log_path(self):
        return self.data.get("log_path", None)

    def log_level(self):
        return self.data.get("log_level", "WARN")

    def results_dir(self):
        return Utils.get_absolute_path(self.data.get("results_dir", None))

    # appium
    def appium_server(self):
        return self.data.get("appium_server", None)

    def platform_name(self):
        return self.data.get("platform_name", None)

    def device_name(self):
        return self.data.get("device_name", None)

    def udid(self):
        return self.data.get("udid", None)

    def app_id(self):
        return self.data.get("app_id", None)

    def app_path(self):
        return Utils.get_absolute_path(self.data.get("app_path", None))

    # appium session behavior
    def app_reinstall(self):
        return bool(self.data.get("app_reinstall", True))

    def app_launch(self):
        return bool(self.data.get("app_launch", True))

    def app_terminate(self):
        return bool(self.data.get("app_terminate", True))

    # custom methods
    def is_ios(self):
        return self.platform_name().lower() == "ios"

    def is_android(self):
        return self.platform_name().lower() == "android"


app = App()
