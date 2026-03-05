"""qis create iot network page"""

from tests.test_base import TestBase
from common import Element, logger, ResultCode, Utils, app, dut


def get_set_up_later_button() -> Element:
    return Element(
        ios_button_name="Set Up Later",
        android_id="com.asus.aihome:id/later_toggle",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/later_toggle"]',
    )


def tap_set_up_later_button(test: TestBase):
    # find set up later button
    set_up_later_button = get_set_up_later_button()

    test.check(
        set_up_later_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Set Up Later button not found",
    )

    test.check(
        set_up_later_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Set Up Later button not tappable",
    )

    logger.info("Tapped 'Set Up Later' button")
