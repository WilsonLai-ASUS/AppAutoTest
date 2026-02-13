# element.py

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

from ..app import app
from .element import Element


class ElementAlert(Element):

    # 如果有帶入輸入, 則使用輸入, 否則使用 IOS_CLASS_CHAIN, '**/XCUIElementTypeAlert'
    def __init__(
        self,
        *,
        web_element=None,
        ios_class_chain='**/XCUIElementTypeAlert',
        ios_predicate_string=None,
        ios_xpath=None,
        android_id='android:id/content',
        android_xpath='//android.widget.FrameLayout[@resource-id="android:id/content"]',
    ):
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
            buttons = self.element.find_elements(
                AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeButton"
            )
            return [Element(web_element=button) for button in buttons]
        except Exception as e:
            pass

        return []

    def element_texts(self) -> list[Element]:
        if not self.is_exist():
            return []

        try:
            texts = self.web_element.find_elements(
                AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeStaticText"
            )
            return [Element(web_element=text) for text in texts]
        except Exception as e:
            pass

        return []

    # alert method

    def title(self) -> str:
        return self.name()

    def body(self) -> str:
        # get last static text element, which is usually the message body
        texts = self.element_texts()
        return texts[-1].name() if texts else ""

    def buttons(self) -> list[str]:
        element_buttons = self.element_buttons()

        if not element_buttons:
            return []

        button_names = [button.name() for button in element_buttons]
        return button_names

    def tap(self, button_name: str) -> bool:
        element_buttons = self.element_buttons()

        for button in element_buttons:
            if button.name() == button_name:
                return button.tap()

        return False
