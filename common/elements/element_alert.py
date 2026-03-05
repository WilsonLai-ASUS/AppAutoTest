# element.py

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

from ..app import app
from .element import Element


class ElementAlert(Element):

    def __init__(
        self,
        *,
        web_element=None,
        ios_class_chain=None,
        ios_predicate_string=None,
        ios_xpath=None,
        ios_name=None,
        android_id="android:id/content",
        android_xpath='//android.widget.FrameLayout[@resource-id="android:id/content"]',
    ):
        if ios_name is not None:
            if not ios_class_chain:
                ios_class_chain = f'**/XCUIElementTypeAlert[`name == "{ios_name}"`]'

            if not ios_predicate_string:
                ios_predicate_string = f'name == "{ios_name}" AND label == "{ios_name}" AND type == "XCUIElementTypeAlert"'

            if not ios_xpath:
                ios_xpath = f'//XCUIElementTypeAlert[@name="{ios_name}"]'

        super().__init__(
            web_element=web_element,
            ios_class_chain=ios_class_chain,
            ios_predicate_string=ios_predicate_string,
            ios_xpath=ios_xpath,
            android_id=android_id,
            android_xpath=android_xpath,
        )

    def element_buttons(self) -> list[Element]:
        if not self.is_exist():
            return []

        try:
            if app.is_ios():
                buttons = self.web_element.find_elements(
                    AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeButton"
                )
            else:
                buttons = self.web_element.find_elements(
                    AppiumBy.XPATH, ".//android.widget.Button"
                )
            return [Element(web_element=button) for button in buttons]
        except Exception as e:
            pass

        return []

    def element_texts(self) -> list[Element]:
        if not self.is_exist():
            return []

        try:
            if app.is_ios():
                texts = self.web_element.find_elements(
                    AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeStaticText"
                )
            else:
                texts = self.web_element.find_elements(
                    AppiumBy.XPATH, ".//android.widget.TextView"
                )
            return [Element(web_element=text) for text in texts]
        except Exception as e:
            pass

        return []

    # alert method

    def title(self) -> str:
        if app.is_android():
            try:
                el = self.web_element.find_element(
                    AppiumBy.XPATH, ".//*[@resource-id='android:id/alertTitle']"
                )
                return el.text or ""
            except Exception:
                return ""
        return self.text()

    def body(self) -> str:
        if app.is_android():
            try:
                el = self.web_element.find_element(
                    AppiumBy.XPATH, ".//*[@resource-id='android:id/message']"
                )
                return el.text or ""
            except Exception:
                texts = self.element_texts()
                return texts[-1].text() if texts else ""

        # iOS: get last static text element, which is usually the message body
        texts = self.element_texts()
        return texts[-1].text() if texts else ""

    def buttons(self) -> list[str]:
        element_buttons = self.element_buttons()

        if not element_buttons:
            return []

        button_names = [button.text() for button in element_buttons]
        return button_names

    def tap(self, button_name: str) -> bool:
        element_buttons = self.element_buttons()

        for button in element_buttons:
            if button.text() == button_name:
                return button.tap()

        return False
