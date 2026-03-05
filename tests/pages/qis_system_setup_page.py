"""qis system setup page"""

from tests.test_base import TestBase
from common import Element, dut, logger, ResultCode, Utils, app, dut


def get_get_started_button() -> Element:
    return Element(ios_button_name="Get Started")


def get_advanced_settings_button() -> Element:
    return Element(
        ios_button_name="Advanced Settings",
        android_id="com.asus.aihome:id/advanced_settings_toggle",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/advanced_settings_toggle"]',
    )


def get_model_name_label(model_name=None) -> Element | None:
    if model_name is None:
        model_name = dut.model_name()

    model_name_label = Element(
        ios_static_text_name=model_name,
        android_id="com.asus.aihome:id/main_title",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/main_title"]',
    )

    if (
        model_name_label
        and model_name_label.is_exist()
        and model_name_label.text() == model_name
    ):
        return model_name_label

    return None


def tap_get_started_button(
    test: TestBase,
    is_wait_wan_detected: bool = True,
):
    # find get started button
    get_started_button = get_get_started_button()

    test.check(
        get_started_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Get Started button not found",
    )

    test.check(
        get_started_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Get Started button not tappable",
    )

    # wait for wan detected
    if is_wait_wan_detected:
        max_wait = 60
        for i in range(max_wait):
            model_name_label = get_model_name_label()
            if model_name_label and model_name_label.is_exist():
                logger.info("WAN Detected")
                break

            logger.info(f"Waiting for WAN Detected... (attempt {i+1}/{max_wait})")
            Utils.delay(1)


def tap_advanced_settings_button(test: TestBase):
    # find advanced settings button
    advanced_settings_button = get_advanced_settings_button()

    test.check(
        advanced_settings_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Advanced Settings button not found",
    )

    test.check(
        advanced_settings_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Advanced Settings button not tappable",
    )

    logger.info("Tapped 'Advanced Settings' button")
