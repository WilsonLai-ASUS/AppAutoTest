"""qis create wifi network page"""

from tests.test_base import TestBase
from common import Element, logger, ResultCode, Utils, app, dut


def get_use_default_local_login_password_button() -> Element:
    return Element(
        ios_class_chain='**/XCUIElementTypeStaticText[`name == "Use default Local Login Password"`][2]',
        ios_xpath='(//XCUIElementTypeStaticText[@name="Use default Local Login Password"])[2]',
    )


def get_ios_username_text_field_clear_text_button() -> Element:
    return Element(ios_button_name="Clear text")


def get_username_text_field() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[1]/XCUIElementTypeTextField",
        ios_xpath="//XCUIElementTypeTextField",
        android_id="com.asus.aihome:id/username_input_field",
        android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/username_input_field"]',
    )


def get_password_text_field() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[2]/XCUIElementTypeSecureTextField",
        ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[2]/XCUIElementTypeSecureTextField",
        android_id="com.asus.aihome:id/pwd_input_field",
        android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/pwd_input_field"]',
    )


def get_confirm_password_text_field() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[3]/XCUIElementTypeSecureTextField",
        ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[3]/XCUIElementTypeSecureTextField",
        android_id="com.asus.aihome:id/confirm_pwd_input_field",
        android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/confirm_pwd_input_field"]',
    )


def get_next_button() -> Element:
    # ios : next
    # android : apply
    return Element(
        ios_class_chain='**/XCUIElementTypeButton[`name == "Next"`][1]',
        ios_xpath='(//XCUIElementTypeButton[@name="Next"])[1]',
        android_id="com.asus.aihome:id/next_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/next_btn"]',
    )


def tap_use_default_local_login_password_button(test: TestBase):
    # find use default local login password button
    use_default_local_login_password_button = (
        get_use_default_local_login_password_button()
    )

    test.check(
        use_default_local_login_password_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Use Default Local Login Password button not found",
    )

    test.check(
        use_default_local_login_password_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Use Default Local Login Password button not tappable",
    )

    logger.info("Tapped 'Use Default Local Login Password' button")


def tap_ios_username_text_field_clear_text_button(test: TestBase):
    # find clear text button
    clear_text_button = get_ios_username_text_field_clear_text_button()

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


def fill_username_text_field(test: TestBase):
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

    logger.info("Tapped 'Username' text field")

    test.check(
        username_text_field.send_keys(dut.local_username()),
        ResultCode.ELEMENT_NOT_INTERACTABLE,
        "Username text field not interactable",
    )

    logger.info(f"Entered 'Username': {dut.local_username()}")


def fill_password_text_field(test: TestBase):
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

    logger.info("Tapped 'Password' text field")

    test.check(
        password_text_field.send_keys(dut.local_password()),
        ResultCode.ELEMENT_NOT_INTERACTABLE,
        "Password text field not interactable",
    )

    logger.info(f"Entered 'Password': {dut.local_password()}")


def fill_confirm_password_text_field(test: TestBase):
    if app.is_android():
        # swipe up to make confirm password text field visible
        test.swipe_up()

    # find confirm password text field
    confirm_password_text_field = get_confirm_password_text_field()

    test.check(
        confirm_password_text_field.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Confirm Password text field not found",
    )

    test.check(
        confirm_password_text_field.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Confirm Password text field not tappable",
    )

    logger.info("Tapped 'Confirm Password' text field")

    test.check(
        confirm_password_text_field.send_keys(dut.local_password()),
        ResultCode.ELEMENT_NOT_INTERACTABLE,
        "Confirm Password text field not interactable",
    )

    logger.info(f"Entered 'Confirm Password': {dut.local_password()}")


def tap_next_button(test: TestBase):
    # find next button
    next_button = get_next_button()

    try:
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

    except Exception as e:
        if app.is_ios():
            # iOS keyboard shrinking event seems to automatically go to the next page
            logger.warn(
                f"Tap Next button failed, maybe it's already on the next page: {e}"
            )
        else:
            raise e

    logger.info("Tapped 'Next' button")
