# element.py

from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy

from ..utils import Utils
from ..app import app
from ..logger import logger


class Element:
    web_element: WebElement | None = None

    def __init__(
        self,
        *,
        web_element=None,
        ios_class_chain=None,
        ios_predicate_string=None,
        ios_xpath=None,
        ios_button_name=None,
        ios_static_text_name=None,
        ios_text_field_name=None,
        ios_name=None,
        android_id=None,
        android_xpath=None,
    ):
        """
        ios priority:
        1. web_element
        2. ios_class_chain
        3. ios_predicate_string
        4. ios_xpath
        5. ios_button_name
        6. ios_name
        7. ios_static_text_name
        8. ios_text_field_name
        9. ios_name

        android priority:
        1. web_element
        2. android_id
        3. android_xpath
        """

        from ..driver import driver

        self.web_element = None

        if web_element is not None:
            self.web_element = web_element
            return

        if app.is_ios():
            # ios_class_chain
            if self.web_element is None and ios_class_chain is not None:
                self.web_element = driver.get_element_by_ios_class_chain(
                    ios_class_chain
                )

            # ios_predicate_string
            if self.web_element is None and ios_predicate_string is not None:
                self.web_element = driver.get_element_by_ios_predicate_string(
                    ios_predicate_string
                )

            # ios_xpath
            if self.web_element is None and ios_xpath is not None:
                self.web_element = driver.get_element_by_xpath(ios_xpath)

            # ios_button_name
            if self.web_element is None and ios_button_name is not None:
                self.web_element = driver.get_element_by_ios_class_chain(
                    f'**/XCUIElementTypeButton[`name == "{ios_button_name}"`]'
                )
                if self.web_element is None:
                    self.web_element = driver.get_element_by_xpath(
                        f'//XCUIElementTypeButton[@name="{ios_button_name}"]'
                    )

            # ios_static_text_name
            if self.web_element is None and ios_static_text_name is not None:
                self.web_element = driver.get_element_by_ios_class_chain(
                    f'**/XCUIElementTypeStaticText[`name == "{ios_static_text_name}"`]'
                )
                if self.web_element is None:
                    self.web_element = driver.get_element_by_xpath(
                        f'//XCUIElementTypeStaticText[@name="{ios_static_text_name}"]'
                    )

            # ios_text_field_name
            if self.web_element is None and ios_text_field_name is not None:
                self.web_element = driver.get_element_by_ios_class_chain(
                    f'**/XCUIElementTypeTextField[`name == "{ios_text_field_name}"`]'
                )
                if self.web_element is None:
                    self.web_element = driver.get_element_by_xpath(
                        f'//XCUIElementTypeTextField[@name="{ios_text_field_name}"]'
                    )

            # ios_name
            if self.web_element is None and ios_name is not None:
                self.web_element = driver.get_element_by_ios_class_chain(
                    f'**/XCUIElementTypeButton[`name == "{ios_name}"`]'
                )
                if self.web_element is None:
                    self.web_element = driver.get_element_by_xpath(
                        f'//XCUIElementTypeButton[@name="{ios_name}"]'
                    )
                    if self.web_element is None:
                        self.web_element = driver.get_element_by_ios_class_chain(
                            f'**/XCUIElementTypeStaticText[`name == "{ios_name}"`]'
                        )
                        if self.web_element is None:
                            self.web_element = driver.get_element_by_xpath(
                                f'//XCUIElementTypeStaticText[@name="{ios_name}"]'
                            )

        elif app.is_android():
            if self.web_element is None and android_id is not None:
                self.web_element = driver.get_element_by_android_id(android_id)

            if self.web_element is None and android_xpath is not None:
                self.web_element = driver.get_element_by_xpath(android_xpath)

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

    def get_parent_element(self) -> "Element":
        if not self.is_exist():
            return Element()

        try:
            if app.is_ios():
                xpath_candidates = [
                    "..",
                    "./..",
                    "parent::*",
                    "./parent::*",
                    "ancestor::*[1]",
                ]
                last_error: Exception | None = None

                for parent_xpath in xpath_candidates:
                    try:
                        parent_web_element = self.web_element.find_element(
                            AppiumBy.XPATH, parent_xpath
                        )
                        parent_element = Element(web_element=parent_web_element)
                        return parent_element
                    except Exception as e:
                        last_error = e

                # Fallback : locate from root then select parent in a single XPath.
                # (More reliable on XCUITest than element->element '..')
                try:
                    from ..driver import driver

                    current = self.debug_attributes()
                    target_tag = current.get("type", "")
                    target_name = current.get("text", "")
                    target_x = current.get("x", None)
                    target_y = current.get("y", None)
                    target_w = current.get("width", None)
                    target_h = current.get("height", None)

                    def _xpath_literal(value: str) -> str:
                        if "'" not in value:
                            return f"'{value}'"
                        if '"' not in value:
                            return f'"{value}"'
                        # Rare: contains both quotes. Minimal safe concat.
                        parts = value.split("'")
                        return (
                            "concat(" + ', "\'", '.join([f"'{p}'" for p in parts]) + ")"
                        )

                    if target_tag and target_name:
                        predicates = [f"@name={_xpath_literal(str(target_name))}"]
                        for attr_name, attr_val in (
                            ("x", target_x),
                            ("y", target_y),
                            ("width", target_w),
                            ("height", target_h),
                        ):
                            if attr_val is not None:
                                predicates.append(f"@{attr_name}='{int(attr_val)}'")

                        current_xpath = (
                            f"//{target_tag}[" + " and ".join(predicates) + "]"
                        )
                        parent_xpath = current_xpath + "/.."
                        parent_web_element = driver.get_element_by_xpath(
                            parent_xpath, timeout=2
                        )
                        if parent_web_element is not None:
                            parent_element = Element(web_element=parent_web_element)
                            return parent_element
                except Exception as e:
                    logger.debug("get_parent_element root-xpath fallback failed: %s", e)
            # TODO : android
        except Exception as e:
            logger.debug("get_parent_element failed: %s", e)
            return Element()

        return Element()

    def rect(self) -> dict:
        return self.web_element.rect if self.is_exist() else {}

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
    def is_exist(self, text=None) -> bool:
        if text is not None:
            return self.web_element is not None and self.text() == text
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

            if delay_after_send > 0:
                Utils.delay(delay_after_send)

            from ..driver import driver

            driver.hide_keyboard()
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

    def rect_by_key(self, rect_name: str) -> int:
        return self.rect().get(rect_name, 0)

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
        return self.rect_by_key("x")

    def y(self) -> int:
        return self.rect_by_key("y")

    def width(self) -> int:
        return self.rect_by_key("width")

    def height(self) -> int:
        return self.rect_by_key("height")

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
