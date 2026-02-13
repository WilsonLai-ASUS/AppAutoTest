# app.py

"""
Configuration utilities for Appium tests.
"""

import json
import os

from .utils import Utils


class App:
    # debug
    log_path = ""
    log_level = "WARNING"
    screenshot_dir = ""

    # appium
    appium_server = ""
    platform_name = ""
    device_name = ""
    udid = ""
    app_id = ""
    app_path = ""

    def __init__(self, path=None):
        if path is not None:
            self.load(path)

    # load

    def load(self, path):
        if not path:
            raise ValueError("App config path is required")

        filepath = Utils.get_absolute_path(path)
        with open(filepath, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid app config file: must be a JSON object")

        # debug
        self.log_path = data.get("log_path", None)
        self.log_level = data.get("log_level", "WARNING")
        self.screenshot_dir = Utils.get_absolute_path(data.get("screenshot_dir", None))

        # appium
        self.appium_server = data.get("appium_server", None)
        self.platform_name = data.get("platform_name", None)
        self.device_name = data.get("device_name", None)
        self.udid = data.get("udid", None)
        self.app_id = data.get("app_id", None)
        self.app_path = Utils.get_absolute_path(data.get("app_path", None))

    def is_ios(self):
        return self.platform_name.lower() == "ios"

    def is_android(self):
        return self.platform_name.lower() == "android"


app = App()
