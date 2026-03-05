"""qis system setup page"""

from tests.test_base import TestBase
from common import (
    Element,
    dut,
    logger,
    ResultCode,
    Utils,
    app,
    dut,
    SystemAlert,
    driver,
)


def get_connect_to_your_wifi_label() -> Element:
    # ios : connect to your wifi
    # android : go to wifi settings
    return Element(
        ios_class_chain='**/XCUIElementTypeStaticText[`name == "Connect to your WiFi"`]',
        ios_xpath='//XCUIElementTypeStaticText[@name="Connect to your WiFi"]',
        android_id="com.asus.aihome:id/go_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/go_btn"]',
    )


def wait_connect_to_your_wifi_label(test: TestBase, timeout=240):
    label_name = "Connect to your WiFi" if app.is_ios() else "Go to WiFi settings"

    for i in range(timeout):
        connect_to_your_wifi_label = get_connect_to_your_wifi_label()
        if connect_to_your_wifi_label.is_exist():
            logger.info(f"'{label_name}' label is displayed")
            Utils.delay(3)
            return

        logger.info(f"Waiting for '{label_name}' label... (attempt {i+1}/{timeout})")
        Utils.delay(1)

    test.check(
        False,
        ResultCode.ELEMENT_NOT_FOUND,
        f"'{label_name}' label not found after waiting",
    )


def tap_ios_join_system_alert_button(test: TestBase, delay_after=30.0):
    # find join system alert
    join_system_alert = SystemAlert()

    test.check(
        join_system_alert.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Join system alert not found",
    )

    test.check(
        join_system_alert.tap("Join"),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Join system alert not tappable",
    )

    logger.info("Tapped 'Join' system alert")

    if delay_after > 0:
        Utils.delay(delay_after)


def connect_android_wifi(test: TestBase):
    # goto android wifi setting page and connect wifi
    test.connect_wifi(dut.wifi_ssid(), dut.wifi_password())
    logger.info("Connected to WiFi in Android system settings")


def reconnect_wifi(test: TestBase):
    if app.is_ios():
        tap_ios_join_system_alert_button(test)
    elif app.is_android():
        connect_android_wifi(test)
