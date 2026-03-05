"""System-level alert helpers.

On iOS we can interact with system alerts via `mobile: alert`.
On Android, runtime permission dialogs are normal UI elements (not Selenium Alerts),
so we detect/tap them by resource-id/text.
"""

from __future__ import annotations

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert

from ..app import app


def get_alert(drv, timeout=1):
    wait = WebDriverWait(drv.web_driver, timeout)
    try:
        alert = wait.until(EC.alert_is_present())
        return alert
    except:
        return None


_ANDROID_PERMISSION_BUTTON_IDS: dict[str, list[str]] = {
    "allow": [
        "com.android.permissioncontroller:id/permission_allow_button",
        "com.android.packageinstaller:id/permission_allow_button",
    ],
    "allow_foreground": [
        "com.android.permissioncontroller:id/permission_allow_foreground_only_button",
        "com.android.packageinstaller:id/permission_allow_foreground_only_button",
    ],
    "allow_one_time": [
        "com.android.permissioncontroller:id/permission_allow_one_time_button",
    ],
    "deny": [
        "com.android.permissioncontroller:id/permission_deny_button",
        "com.android.packageinstaller:id/permission_deny_button",
    ],
}

_ANDROID_TEXT_IDS: list[str] = [
    "com.android.permissioncontroller:id/permission_message",
    "com.android.permissioncontroller:id/permission_title",
    "android:id/message",
    "android:id/alertTitle",
]


class SystemAlert:
    alert: Alert | None = None

    def __init__(self):
        from ..driver import driver

        self.alert = get_alert(driver) if app.is_ios() else None

    def _android_find_by_id(self, resource_id: str):
        from ..driver import driver

        try:
            el = driver.get_element_by_xpath(
                f"//*[@resource-id='{resource_id}']",
                timeout=1,
            )
            return el
        except Exception:
            return None

    def _android_tap_first_existing_id(self, ids: list[str]) -> bool:
        for rid in ids:
            el = self._android_find_by_id(rid)
            try:
                if el and el.is_displayed():
                    el.click()
                    return True
            except Exception:
                pass
        return False

    def _android_any_permission_button_exists(self) -> bool:
        for ids in _ANDROID_PERMISSION_BUTTON_IDS.values():
            for rid in ids:
                el = self._android_find_by_id(rid)
                try:
                    if el and el.is_displayed():
                        return True
                except Exception:
                    pass
        return False

    def is_exist(self) -> bool:
        if app.is_android():
            return self._android_any_permission_button_exists()
        return self.alert is not None

    def text(self) -> str:
        if not self.is_exist():
            return ""

        if app.is_android():
            for rid in _ANDROID_TEXT_IDS:
                el = self._android_find_by_id(rid)
                try:
                    if el and el.is_displayed():
                        return el.text or ""
                except Exception:
                    pass
            return ""

        return self.alert.text if self.alert is not None else ""

    # alert method

    def title(self) -> str:
        parts = self.text().split(
            "\n", 1
        )  # iOS 的系統 Alert 通常會把 title 和 message 用換行分隔，所以我們取第一行當作 title
        return parts[0] if parts else ""

    def body(self) -> str:
        parts = self.text().split(
            "\n", 1
        )  # iOS 的系統 Alert 通常會把 title 和 message 用換行分隔，所以我們取第二行當作 body
        return parts[1] if len(parts) > 1 else ""

    def buttons(self) -> list[str]:
        from ..driver import driver

        if app.is_android():
            labels: list[str] = []
            for ids in _ANDROID_PERMISSION_BUTTON_IDS.values():
                for rid in ids:
                    el = self._android_find_by_id(rid)
                    try:
                        if el and el.is_displayed():
                            t = (el.text or "").strip()
                            if t:
                                labels.append(t)
                    except Exception:
                        pass
            # De-dupe while preserving order
            out: list[str] = []
            for t in labels:
                if t not in out:
                    out.append(t)
            return out

        try:
            buttons = driver.web_driver.execute_script(
                "mobile: alert", {"action": "getButtons"}
            )
            return buttons if buttons else []
        except Exception:
            return []

    def tap(self, button_name: str) -> bool:
        from ..driver import driver

        if app.is_android():
            # Try by exact visible text first.
            try:
                el = driver.get_element_by_xpath(
                    f"//*[@text=\"{button_name}\" or @content-desc=\"{button_name}\"]",
                    timeout=1,
                )
                if el and el.is_displayed():
                    el.click()
                    return True
            except Exception:
                pass
            return False

        try:
            driver.web_driver.execute_script(
                "mobile: alert", {"action": "accept", "buttonLabel": button_name}
            )
            return True
        except Exception:
            return False

    def tap_allow(self) -> bool:
        if app.is_android():
            # Prefer foreground-only (common on Android 10+), then Allow, then One-time.
            return (
                self._android_tap_first_existing_id(_ANDROID_PERMISSION_BUTTON_IDS["allow_foreground"])
                or self._android_tap_first_existing_id(_ANDROID_PERMISSION_BUTTON_IDS["allow"])
                or self._android_tap_first_existing_id(_ANDROID_PERMISSION_BUTTON_IDS["allow_one_time"])
            )
        return self.tap("Allow")

    def tap_allow_while_using_app(self) -> bool:
        if app.is_android():
            return self._android_tap_first_existing_id(
                _ANDROID_PERMISSION_BUTTON_IDS["allow_foreground"]
            )
        return self.tap("Allow While Using App")
