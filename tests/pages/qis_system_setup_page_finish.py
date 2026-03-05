"""qis system setup finish page"""

from tests.test_base import TestBase
from common import Element, dut, logger, ResultCode, Utils, app, dut


def get_finish_button() -> Element:
    return Element(
        ios_button_name="Finish",
        android_id="com.asus.aihome:id/finish_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/finish_btn"]',
    )


def wait_finish_button(test: TestBase, timeout=120):
    found_finish_flag = False

    for i in range(timeout):
        finish_button = get_finish_button()
        if finish_button.is_exist():
            logger.info("Finish button is displayed")
            found_finish_flag = True
            break

        logger.info(f"Waiting for Finish button... (attempt {i+1}/{timeout})")
        Utils.delay(1)

    test.check(
        found_finish_flag,
        ResultCode.ELEMENT_NOT_FOUND,
        ("Finish button not found"),
    )


def tap_finish_button(test: TestBase):
    # find finish button
    finish_button = get_finish_button()

    test.check(
        finish_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Finish button not found",
    )

    test.check(
        finish_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Finish button not tappable",
    )
