# elementFinderMixin.py

from .element import Element

# template
"""
        @staticmethod
        def get_xxx() -> Element:
            return Element(
                ios_class_chain='',
                ios_predicate_string='',
                ios_xpath='',
                android_id="",
                android_xpath='',
            )
"""


class ElementFinder:

    class AsusEulaPage:
        @staticmethod
        def get_title_bar() -> Element:
            return Element(
                ios_class_chain='**/XCUIElementTypeStaticText[`name == "End User License Agreement"`]',
                ios_predicate_string='name == "End User License Agreement" AND label == "End User License Agreement" AND value == "End User License Agreement"',
                ios_xpath='//XCUIElementTypeStaticText[@name="End User License Agreement"]',
                android_id="com.asus.aihome:id/title",
                android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/title"]',
            )

        @staticmethod
        def get_scroll_view() -> Element:
            return Element(
                ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeScrollView",
                ios_predicate_string='type == "XCUIElementTypeScrollView"',
                ios_xpath="//XCUIElementTypeScrollView",
                android_id="com.asus.aihome:id/scroll_view",
                android_xpath='//android.widget.ScrollView[@resource-id="com.asus.aihome:id/scroll_view"]',
            )

        @staticmethod
        def get_above_16_button() -> Element:
            return Element(
                ios_class_chain='**/XCUIElementTypeButton[`name == "I am above the age of 16 years."`]',
                ios_predicate_string='name == "I am above the age of 16 years." AND label == "I am above the age of 16 years." AND type == "XCUIElementTypeButton"',
                ios_xpath='//XCUIElementTypeButton[@name="I am above the age of 16 years."]',
                android_id="com.asus.aihome:id/age",
                android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/age"]',
            )

        @staticmethod
        def get_agree_button() -> Element:
            return Element(
                ios_class_chain='**/XCUIElementTypeButton[`name == "Agree"`]',
                ios_predicate_string='name == "Agree" AND label == "Agree" AND type == "XCUIElementTypeButton"',
                ios_xpath='//XCUIElementTypeButton[@name="Agree"]',
                android_id="com.asus.aihome:id/agree",
                android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/agree"]',
            )

    class AsusPrivacyPolicyPage:
        @staticmethod
        def get_title_bar() -> Element:
            return Element(
                ios_class_chain='**/XCUIElementTypeStaticText[`name == "ASUS PRIVACY NOTICE"`]',
                ios_predicate_string='name == "ASUS PRIVACY NOTICE" AND label == "ASUS PRIVACY NOTICE"',
                ios_xpath='//XCUIElementTypeStaticText[@name="ASUS PRIVACY NOTICE"]',
                android_id="com.asus.aihome:id/title",
                android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/title"]',
            )

        @staticmethod
        def get_scroll_view() -> Element:
            return Element(
                ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeScrollView",
                ios_predicate_string='type == "XCUIElementTypeScrollView"',
                ios_xpath="//XCUIElementTypeScrollView",
                android_id="com.asus.aihome:id/scroll_view",
                android_xpath='//android.widget.ScrollView[@resource-id="com.asus.aihome:id/scroll_view"]',
            )

        @staticmethod
        def get_agree_button() -> Element:
            return Element(
                ios_class_chain='**/XCUIElementTypeButton[`name == "Agree"`]',
                ios_predicate_string='name == "Agree" AND label == "Agree" AND type == "XCUIElementTypeButton"',
                ios_xpath='//XCUIElementTypeButton[@name="Agree"]',
                android_id="com.asus.aihome:id/agree",
                android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/agree"]',
            )


    