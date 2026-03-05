"""qis manual setup page"""

from tests.test_base import TestBase
from common import Element, dut, logger, ResultCode, Utils, app, dut


def get_get_dhcp_button() -> Element:
    return Element(
        ios_name="DHCP (Default)",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/wan_type_title" and @text="DHCP"]',
    )


def get_next_button() -> Element:
    return Element(
        ios_button_name="Next",
        android_id='com.asus.aihome:id/next_btn',
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/next_btn"]',
    )


def tap_dhcp_button(test: TestBase):
    # find get dhcp button
    get_dhcp_button = get_get_dhcp_button()

    test.check(
        get_dhcp_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "DHCP (Default) button not found",
    )

    test.check(
        get_dhcp_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "DHCP (Default) button not tappable",
    )

    logger.info("Tapped 'DHCP (Default)' button")


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
