# alert.py

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert

from ..utils import Utils
from ..app import app


def get_alert(driver, timeout=1):
    wait = WebDriverWait(driver.web_driver, timeout)
    try:
        alert = wait.until(EC.alert_is_present())
        return alert
    except:
        return None


class SystemAlert:
    alert: Alert | None = None

    def __init__(self):
        from ..driver import driver

        self.alert = get_alert(driver)

    def is_exist(self) -> bool:
        return self.alert is not None

    def text(self) -> str:
        return self.alert.text if self.is_exist() else ""

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
        from .driver import driver

        try:
            buttons = driver.web_driver.execute_script(
                "mobile: alert", {"action": "getButtons"}
            )
            return buttons if buttons else []
        except Exception as e:
            return []

    def tap(self, button_name: str) -> bool:
        from .driver import driver

        try:
            driver.web_driver.execute_script(
                "mobile: alert", {"action": "accept", "buttonLabel": button_name}
            )
            return True
        except Exception as e:
            return False

    def tap_allow(self) -> bool:
        return self.tap("Allow")

    def tap_allow_while_using_app(self) -> bool:
        return self.tap("Allow While Using App")
