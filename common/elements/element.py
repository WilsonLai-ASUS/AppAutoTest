# element.py

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from ..utils import Utils
from ..app import app


def get_elements_by_ios_predicate_string(driver, predicate_string, timeout=1):
    try:
        return driver.web_driver.find_elements(AppiumBy.IOS_PREDICATE, predicate_string)
    except:
        return []  # 找不到元素就回傳空 list


def get_element_by_ios_predicate_string(driver, predicate_string, timeout=1):
    elements = get_elements_by_ios_predicate_string(driver, predicate_string, timeout)
    return elements[-1] if elements else None


def get_elements_by_ios_class_chain(driver, class_chain, timeout=1):
    try:
        return driver.web_driver.find_elements(AppiumBy.IOS_CLASS_CHAIN, class_chain)
    except:
        return []  # 找不到元素就回傳空 list


def get_element_by_ios_class_chain(driver, class_chain, timeout=1):
    elements = get_elements_by_ios_class_chain(driver, class_chain, timeout)
    return elements[-1] if elements else None


def get_elements_by_android_id(driver, android_id, timeout=1):
    try:
        return driver.web_driver.find_elements(AppiumBy.ID, android_id)
    except:
        return []  # 找不到元素就回傳空 list


def get_element_by_android_id(driver, android_id, timeout=1):
    elements = get_elements_by_android_id(driver, id, timeout)
    return elements[-1] if elements else None


def get_elements_by_xpath(driver, xpath, timeout=1):
    wait = WebDriverWait(driver.web_driver, timeout)
    try:
        elements = wait.until(
            EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath))
        )
        return elements  # list，可能有多個元素
    except:
        return []  # 找不到元素就回傳空 list


def get_element_by_xpath(driver, xpath, timeout=1):
    elements = get_elements_by_xpath(driver, xpath, timeout)
    return elements[-1] if elements else None  # 回傳最後一個元素，如果找不到就回傳 None


class Element:
    web_element: WebElement | None = None

    def __init__(
        self,
        *,
        web_element=None,
        ios_class_chain=None,
        ios_predicate_string=None,
        ios_xpath=None,
        android_id=None,
        android_xpath=None,
    ):
        from ..driver import driver

        self.web_element = None

        if web_element is not None:
            self.web_element = web_element
            return

        if app.is_ios():
            if self.web_element is None and ios_class_chain is not None:
                self.web_element = get_element_by_ios_class_chain(
                    driver, ios_class_chain
                )

            if self.web_element is None and ios_predicate_string is not None:
                self.web_element = get_element_by_ios_predicate_string(
                    driver, ios_predicate_string
                )

            if self.web_element is None and ios_xpath is not None:
                self.web_element = get_element_by_xpath(driver, ios_xpath)

        elif app.is_android():
            if self.web_element is None and android_id is not None:
                self.web_element = get_element_by_android_id(driver, android_id)

            if self.web_element is None and android_xpath is not None:
                self.web_element = get_element_by_xpath(driver, android_xpath)

    # get attributes
    def get_attribute_str(self, attribute_name: str) -> str:
        if self.is_exist():
            try:
                value = self.web_element.get_attribute(attribute_name)
                return str(value) if value is not None else ""
            except:
                return ""
        return ""

    def get_attribute_int(self, attribute_name: str) -> int:
        attribute_value = self.get_attribute_str(attribute_name)
        try:
            return int(attribute_value)
        except:
            return 0

    def get_attribute_bool(self, attribute_name: str) -> bool:
        attribute_value = self.get_attribute_str(attribute_name)
        return attribute_value.lower() == "true"

    def rect(self, rect_name: str) -> int:
        return self.web_element.rect.get(rect_name, 0) if self.is_exist() else 0

    def is_displayed(self) -> bool:
        return self.web_element.is_displayed() if self.is_exist() else False

    def is_enabled(self) -> bool:
        return self.web_element.is_enabled() if self.is_exist() else False

    # ios default attributes (A ~ Z)
    def _ios_accessible(self) -> bool:
        return self.get_attribute_bool("accessible")

    def _ios_element_id(self) -> str:
        return self.get_attribute_str("elementId")

    def _ios_height(self) -> int:
        return self.web_element.rect.get("height", 0) if self.is_exist() else 0

    def _ios_name(self) -> str:
        return self.get_attribute_str("name")

    def _ios_type(self) -> str:
        return self.get_attribute_str("type")

    def _ios_width(self) -> int:
        return self.web_element.rect.get("width", 0) if self.is_exist() else 0

    def _ios_x(self) -> int:
        return self.web_element.rect.get("x", 0) if self.is_exist() else 0

    def _ios_y(self) -> int:
        return self.web_element.rect.get("y", 0) if self.is_exist() else 0

    # android default attributes (A ~ Z)
    def _android_class(self) -> str:
        return self.get_attribute_str("class")

    def _android_text(self) -> str:
        return self.get_attribute_str("text")

    # custom attributes
    def is_exist(self) -> bool:
        return self.web_element is not None

    def tap(self, delay_after_tap=1) -> bool:
        if not self.is_exist():
            return False

        try:
            self.web_element.click()
            Utils.delay(delay_after_tap)
            return True
        except Exception as e:
            return False

    def send_keys(self, text: str, delay_after_send=1) -> bool:
        if not self.is_exist():
            return False

        try:
            self.web_element.send_keys(text)
            Utils.delay(delay_after_send)
            return True
        except Exception as e:
            return False

    def type(self) -> str:
        if app.is_ios():
            return self._ios_type()
        elif app.is_android():
            return self._android_class()
        else:
            return ""

    # custom attributes - text
    def text(self) -> str:
        if app.is_ios():
            return self._ios_name()
        elif app.is_android():
            return self._android_text()
        else:
            return ""

    # custom attributes - position and size
    def center_x(self) -> int:
        return self.x() + self.width() // 2

    def center_y(self) -> int:
        return self.y() + self.height() // 2

    def x(self) -> int:
        return self.rect("x")

    def y(self) -> int:
        return self.rect("y")

    def width(self) -> int:
        return self.rect("width")

    def height(self) -> int:
        return self.rect("height")

    # custom attributes - type checks
    def is_type(self, type: str) -> bool:
        return self.type() == type

    def is_alert_type(self) -> bool:
        return self.is_type("XCUIElementTypeAlert")  # TODO: andoird alert type

    # custom attributes - debug
    def debug_attributes(self) -> dict:
        attributes = {
            "type": self.type(),
            "text": self.text(),
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
            "center_x": self.center_x(),
            "center_y": self.center_y(),
            "is_alert_type": self.is_alert_type(),
        }
        return attributes
