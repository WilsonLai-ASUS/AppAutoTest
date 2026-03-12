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

    def wifi_ssid(self, band: str | None = None):
        ssid = self.data.get("wifi_ssid", None)
        # SSID_2G, SSID_5G, SSID_5G1, SSID_5G2, SSID_6G, SSID_6G1, SSID_6G2
        if ssid is not None and band is not None:
            ssid += "_" + band.upper()
        return ssid

    def wifi_password(self, band: str | None = None):
        # always return the same password for different bands since currently we only have one password field in dut config, and the password is the same for different bands in real case
        return self.data.get("wifi_password", None)

    # feature support
    def bands(self) -> list[str]:
        band = self.data.get("bands", "")
        if band:
            return [b.strip() for b in band.split("/")]
        return []

    def is_qis_support_default_password(self):
        return self.data.get("is_qis_support_default_password", False)

    def is_qis_support_separate_ssid(self):
        return self.data.get("is_qis_support_separate_ssid", False)

    def is_qis_support_isp(self):
        return self.data.get("is_qis_support_isp", False)

    def is_qis_support_create_iot_network(self):
        return self.data.get("is_qis_support_create_iot_network", False)

    def is_support_2g(self):
        return "2g" in self.bands()

    def is_support_5g(self):
        return "5g" in self.bands()

    def is_support_5g1(self):
        return "5g1" in self.bands()

    def is_support_5g2(self):
        return "5g2" in self.bands()

    def is_support_6g(self):
        return "6g" in self.bands()

    def is_support_6g1(self):
        return "6g1" in self.bands()

    def is_support_6g2(self):
        return "6g2" in self.bands()


dut = Dut()
