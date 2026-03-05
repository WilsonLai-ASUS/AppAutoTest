"""qis create wifi network page"""

from tests.test_base import TestBase
from common import Element, logger, ResultCode, Utils, app, dut


def get_ios_wifi_network_name_text_field_clear_text_button() -> Element:
    return Element(ios_button_name="Clear text")


def get_ios_wifi_network_password_text_field_show_password_button() -> Element:
    return Element(ios_button_name="Show Password")


def get_wifi_network_name_text_field() -> Element:
    if app.is_ios():
        clear_text_button = get_ios_wifi_network_name_text_field_clear_text_button()
        return clear_text_button.get_parent_element()
    elif app.is_android():
        return Element(
            android_id="com.asus.aihome:id/ssid_24g_input_field",
            android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/ssid_24g_input_field"]',
        )
    else:
        return Element()


def get_wifi_network_password_text_field() -> Element:
    if app.is_ios():
        show_password_button = (
            get_ios_wifi_network_password_text_field_show_password_button()
        )
        return show_password_button.get_parent_element()
    elif app.is_android():
        return Element(
            android_id="com.asus.aihome:id/pwd_24g_input_field",
            android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/pwd_24g_input_field"]',
        )
    else:
        return Element()


def get_next_button() -> Element:
    return Element(
        ios_button_name="Next",
        android_id="com.asus.aihome:id/next_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/next_btn"]',
    )


def tap_ios_wifi_network_name_clear_text_button(test: TestBase):
    # find clear text button
    clear_text_button = get_ios_wifi_network_name_text_field_clear_text_button()

    test.check(
        clear_text_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Clear text button not found",
    )

    test.check(
        clear_text_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Clear text button not tappable",
    )

    logger.info("Tapped 'Clear text' button")


def fill_wifi_network_name_text_field(test: TestBase):
    # find wifi network name text field
    wifi_network_name_text_field = get_wifi_network_name_text_field()

    test.check(
        wifi_network_name_text_field.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Wi-Fi network name text field not found",
    )

    test.check(
        wifi_network_name_text_field.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Wi-Fi network name text field not tappable",
    )

    logger.info("Tapped Wi-Fi network name text field")

    test.check(
        wifi_network_name_text_field.send_keys(dut.wifi_ssid()),
        ResultCode.ELEMENT_NOT_INTERACTABLE,
        "Wi-Fi network name text field not interactable",
    )

    logger.info(f"Entered Wi-Fi network name: {dut.wifi_ssid()}")


def fill_wifi_network_password_text_field(test: TestBase):
    # find wifi network password text field
    wifi_network_password_text_field = get_wifi_network_password_text_field()

    test.check(
        wifi_network_password_text_field.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Wi-Fi network password text field not found",
    )

    test.check(
        wifi_network_password_text_field.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Wi-Fi network password text field not tappable",
    )

    logger.info("Tapped Wi-Fi network password text field")

    test.check(
        wifi_network_password_text_field.send_keys(dut.wifi_password()),
        ResultCode.ELEMENT_NOT_INTERACTABLE,
        "Wi-Fi network password text field not interactable",
    )

    logger.info(f"Entered Wi-Fi network password: {dut.wifi_password()}")


def tap_next_button(test: TestBase):
    # find next button
    next_button = get_next_button()

    test.check(
        next_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Next button not found",
    )

    test.check(
        next_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Next button not tappable",
    )

    logger.info("Tapped 'Next' button")
