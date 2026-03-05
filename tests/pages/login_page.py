"""login page"""

from tests.test_base import TestBase
from common import dut, Element, logger, ResultCode, Utils


def get_username_text_field() -> Element:
    return Element(
        ios_class_chain='**/XCUIElementTypeTextField[`value == "Username"`]',
        ios_predicate_string='value == "Username"',
        ios_xpath='//XCUIElementTypeTextField[@value="Username"]',
        android_id="com.asus.aihome:id/username_input_field",
        android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/username_input_field"]',
    )


def get_password_text_field() -> Element:
    return Element(
        ios_class_chain="XCUIElementTypeSecureTextField",
        ios_predicate_string='value == "Password"',
        ios_xpath='//XCUIElementTypeSecureTextField[@value="Password"]',
        android_id="com.asus.aihome:id/key_input_field",
        android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/key_input_field"]',
    )


def get_login_button() -> Element:
    return Element(
        ios_class_chain='**/XCUIElementTypeButton[`name == "Sign in"`]',
        ios_predicate_string='name == "Sign in" AND label == "Sign in" AND type == "XCUIElementTypeButton"',
        ios_xpath='//XCUIElementTypeButton[@name="Sign in"]',
        android_id="com.asus.aihome:id/action_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/action_btn"]',
    )


def login(test: TestBase):
    input_username(test)
    input_password(test)
    tap_login_button(test)


def input_username(test: TestBase):
    # find username text field
    username_text_field = get_username_text_field()

    test.check(
        username_text_field.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Username text field not found",
    )

    test.check(
        username_text_field.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Username text field not tappable",
    )

    test.check(
        username_text_field.send_keys(dut.local_username()),
        ResultCode.ELEMENT_NOT_TYPABLE,
        "Username text field not typable",
    )


def input_password(test: TestBase):
    # find password text field
    password_text_field = get_password_text_field()

    test.check(
        password_text_field.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Password text field not found",
    )

    test.check(
        password_text_field.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Password text field not tappable",
    )

    test.check(
        password_text_field.send_keys(dut.local_password()),
        ResultCode.ELEMENT_NOT_TYPABLE,
        "Password text field not typable",
    )


def tap_login_button(test: TestBase):
    # find login button
    login_button = get_login_button()

    test.check(
        login_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Login button not found",
    )

    test.check(
        login_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Login button not tappable",
    )

    Utils.delay(4)
