"""qis create wifi network page"""

from tests.test_base import TestBase
from common import Element, driver, logger, ResultCode, Utils, app, dut


def get_page_title_label() -> Element:
    return Element(
        ios_name="Create WiFi Network",
        android_id="com.asus.aihome:id/main_title",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/main_title"]',
    )


def get_ios_wifi_network_name_text_field_clear_text_button() -> Element:
    return Element(ios_button_name="Clear text")


def get_ios_wifi_network_password_text_field_show_password_button() -> Element:
    return Element(ios_button_name="Show Password")


def get_wifi_network_name_text_field(band: str | None = None) -> Element:
    if app.is_ios():
        if band is None:
            clear_text_button = get_ios_wifi_network_name_text_field_clear_text_button()
            return clear_text_button.get_parent_element()
        else:
            if band == "2g":
                return Element(
                    ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[1]/XCUIElementTypeTextField",
                    ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[1]/XCUIElementTypeTextField",
                )
            elif band == "5g":
                return Element(
                    ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[3]/XCUIElementTypeTextField",
                    ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[3]/XCUIElementTypeTextField",
                )
    elif app.is_android():
        if band is None:
            element1 = Element(
                android_id="com.asus.aihome:id/ssid_24g_input_field",
                android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/ssid_24g_input_field"]',
            )

            if element1.is_exist():
                return element1

            default_wifi_ssid = dut.default_wifi_ssid()

            element2 = Element(
                android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/input_edit" and @text="{default_wifi_ssid}"]'.format(
                    default_wifi_ssid=default_wifi_ssid
                )
            )
            if element2.is_exist():
                return element2
        else:
            logger.warning(
                "Separate SSID is not supported on Android QIS, cannot get wifi network name text field for band %s",
                band,
            )
            # TODO

    return Element()


def get_wifi_network_password_text_field(band: str | None = None) -> Element:
    if app.is_ios():
        if band is None:
            show_password_button = (
                get_ios_wifi_network_password_text_field_show_password_button()
            )
            return show_password_button.get_parent_element()
        else:
            if band == "2g":
                return Element(
                    ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[2]/XCUIElementTypeSecureTextField",
                    ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[2]/XCUIElementTypeSecureTextField",
                )
            elif band == "5g":
                return Element(
                    ios_class_chain="**/XCUIElementTypeWindow/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[4]/XCUIElementTypeSecureTextField",
                    ios_xpath="//XCUIElementTypeTable/XCUIElementTypeCell[4]/XCUIElementTypeSecureTextField",
                )
    elif app.is_android():
        if band is None:
            element1 = Element(
                android_id="com.asus.aihome:id/pwd_24g_input_field",
                android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/pwd_24g_input_field"]',
            )

            if element1.is_exist():
                return element1

            default_wifi_password = dut.default_wifi_password()

            element2 = Element(
                android_xpath='//android.widget.EditText[@resource-id="com.asus.aihome:id/input_edit" and @text="{default_wifi_password}"]'.format(
                    default_wifi_password=default_wifi_password
                )
            )
            if element2.is_exist():
                return element2
        else:
            logger.warning(
                "Separate SSID is not supported on Android QIS, cannot get wifi network password text field for band %s",
                band,
            )
            # TODO

    return Element()


def get_next_button() -> Element:
    return Element(
        ios_button_name="Next",
        android_id="com.asus.aihome:id/next_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/next_btn"]',
    )


def is_page_displayed() -> bool:
    page_title_label = get_page_title_label()

    if app.is_ios():
        return page_title_label.is_exist()
    else:
        return page_title_label.text_equals("Create WiFi Network")


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
    if dut.is_qis_support_separate_ssid() == False:
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
    # seperate ssid case
    else:
        for band in dut.bands():
            wifi_network_name_text_field = get_wifi_network_name_text_field(band)

            test.check(
                wifi_network_name_text_field.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                f"Wi-Fi network name {band} text field not found",
            )

            test.check(
                wifi_network_name_text_field.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                f"Wi-Fi network name {band} text field not tappable",
            )

            logger.info(f"Tapped Wi-Fi network name {band} text field")

            test.check(
                wifi_network_name_text_field.clear_text(),
                ResultCode.ELEMENT_NOT_INTERACTABLE,
                f"Wi-Fi network name {band} text field not interactable for clear text",
            )

            test.check(
                wifi_network_name_text_field.send_keys(dut.wifi_ssid(band)),
                ResultCode.ELEMENT_NOT_INTERACTABLE,
                f"Wi-Fi network name {band} text field not interactable for send keys",
            )

            logger.info(
                f"Entered Wi-Fi network name: {dut.wifi_ssid(band)} for band {band}"
            )


def fill_wifi_network_password_text_field(test: TestBase):
    # find wifi network password text field
    if dut.is_qis_support_separate_ssid() == False:
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
    # seperate ssid case
    else:
        for band in dut.bands():
            wifi_network_password_text_field = get_wifi_network_password_text_field(
                band
            )

            test.check(
                wifi_network_password_text_field.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                f"Wi-Fi network password {band} text field not found",
            )

            test.check(
                wifi_network_password_text_field.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                f"Wi-Fi network password {band} text field not tappable",
            )

            logger.info(f"Tapped Wi-Fi network password {band} text field")

            test.check(
                wifi_network_password_text_field.clear_text(),
                ResultCode.ELEMENT_NOT_INTERACTABLE,
                f"Wi-Fi network password {band} text field not interactable for clear text",
            )

            test.check(
                wifi_network_password_text_field.send_keys(dut.wifi_password(band)),
                ResultCode.ELEMENT_NOT_INTERACTABLE,
                f"Wi-Fi network password {band} text field not interactable for send keys",
            )

            logger.info(
                f"Entered Wi-Fi network password: {dut.wifi_password(band)} for band {band}"
            )


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
