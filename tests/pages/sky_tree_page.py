"""login page"""

from tests.test_base import TestBase
from common import Element, app, logger, ResultCode, Utils


def get_setup_button() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[1]",
        ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[1]",
        android_id="com.asus.aihome:id/qis_zone",
        android_xpath='//android.widget.LinearLayout[@resource-id="com.asus.aihome:id/qis_zone"]',
    )


def get_login_button() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[2]",
        ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[2]",
        android_id="com.asus.aihome:id/sign_zone",
        android_xpath='//android.widget.LinearLayout[@resource-id="com.asus.aihome:id/sign_zone"]',
    )


def tap_login_button(test: TestBase):
    Utils.delay(4)

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

    logger.info("Tapped 'Login' button")

    Utils.delay(4)


def tap_setup_button(test: TestBase):
    if app.is_ios():
        Utils.delay(10)
    else:
        Utils.delay(5)

    # find setup button
    setup_button = get_setup_button()

    test.check(
        setup_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Setup button not found",
    )

    test.check(
        setup_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Setup button not tappable",
    )

    logger.info("Tapped 'Setup' button")

    Utils.delay(4)
