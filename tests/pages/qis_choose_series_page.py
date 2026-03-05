"""qis choose series page"""

from tests.test_base import TestBase
from common import Element, logger, ResultCode, Utils, app, dut, SystemAlert
import tests.pages.qis_system_setup_page as qis_system_setup_page


def get_ios_asus_wifi_7_series_button() -> Element:
    return Element(
        ios_name="ASUS WiFi7 series For example ZenWiFi BQ16 Pro, BT10, BD4, RT-BE58 Go, RT-BE88U, GT-BE25000, etc."
    )


def get_asus_zenwifi_series_button() -> Element:
    return Element(
        ios_name="ASUS WiFi4/5/6 series For example ZenWiFi AC, Pro XT12/ET12, AX, XT9, RT-AX56U, RT-AX86U Pro, etc."
    )


def get_android_asus_wifi_routers_button() -> Element:
    return Element(
        android_id="",
        android_xpath='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.asus.aihome:id/recycler_view"]/android.widget.RelativeLayout[1]',
    )


def get_android_asus_zenwifi_series_button() -> Element:
    return Element(
        android_id="",
        android_xpath='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.asus.aihome:id/recycler_view"]/android.widget.RelativeLayout[2]',
    )


def get_asus_lyra_series_button() -> Element:
    return Element(
        ios_name="ASUS Lyra series For example Lyra, Lyra Mini, Lyra Trio, Lyra Voice",
        android_id="",
        android_xpath='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.asus.aihome:id/recycler_view"]/android.widget.RelativeLayout[3]',
    )


def get_android_app_permissions_ok_button() -> Element:
    return Element(
        android_id="com.asus.aihome:id/go_next_btn",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/go_next_btn"]',
    )


def get_android_close_button() -> Element:
    return Element(
        android_xpath='//android.widget.ImageButton[@content-desc="Close"]',
    )


def get_android_back_button() -> Element:
    return Element(
        android_xpath='//android.widget.ImageButton[@content-desc="Navigate up"]',
    )


def get_android_select_manually_button() -> Element:
    return Element(
        android_id="com.asus.aihome:id/btn_back",
        android_xpath='//android.widget.Button[@resource-id="com.asus.aihome:id/btn_back"]',
    )


def get_android_ssid_text_view(ssid) -> Element:
    element = Element(
        android_xpath=f'//android.widget.TextView[@resource-id="com.asus.aihome:id/device_name" and @text="{ssid} (Connected)"]',
    )
    return (
        element
        if element.is_exist()
        else Element(
            android_xpath=f'//android.widget.TextView[@resource-id="com.asus.aihome:id/device_name" and @text="{ssid}"]',
        )
    )


def tap_ios_asus_wifi_7_series(test: TestBase, is_wait_device_discovery=True):
    # find asus wifi 7 series button
    asus_wifi_7_series_button = get_ios_asus_wifi_7_series_button()

    test.check(
        asus_wifi_7_series_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "ASUS WiFi 7 series button not found",
    )

    test.check(
        asus_wifi_7_series_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "ASUS WiFi 7 series button not tappable",
    )

    logger.info("Tapped 'ASUS WiFi 7 series' button")

    if is_wait_device_discovery:
        retry = 10
        for i in range(retry):
            model_name_label = qis_system_setup_page.get_model_name_label()
            if model_name_label and model_name_label.is_exist():
                logger.info("Device discovery completed")
                break
            logger.debug(f"Waiting for device discovery... (attempt {i+1}/{retry})")
            Utils.delay(3)
        else:
            logger.warn("Device discovery may not have completed after waiting")


def tap_android_asus_wifi_routers(
    test: TestBase, is_allow_app_permissions_alert=True, is_wait_device_discovery=True
):
    # find asus wifi routers button
    asus_wifi_routers_button = get_android_asus_wifi_routers_button()

    test.check(
        asus_wifi_routers_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "ASUS WiFi Routers button not found",
    )

    test.check(
        asus_wifi_routers_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "ASUS WiFi Routers button not tappable",
    )

    logger.info("Tapped 'ASUS WiFi Routers' button")

    Utils.delay(1)

    if is_allow_app_permissions_alert:
        if is_android_app_permissions_alert_exist(test):
            tap_android_app_permissions_ok_button(test)
            tap_android_location_permission_system_alert_allow_button(test)
            Utils.delay(5)

            # handle android bug
            if True:
                is_close_button_tapped = False

                try:
                    android_close_button = get_android_close_button()
                    if android_close_button.is_exist():
                        android_close_button.tap()
                        is_close_button_tapped = True
                        logger.info("Tapped Android system alert 'Close' button")
                except Exception as e:
                    pass

                if not is_close_button_tapped:
                    try:
                        android_back_button = get_android_back_button()
                        if android_back_button.is_exist():
                            android_back_button.tap()
                            is_close_button_tapped = True
                            logger.info(
                                "Tapped Android system alert 'Back' button to workaround the bug"
                            )
                    except Exception as e:
                        pass

                test.check(
                    is_close_button_tapped,
                    ResultCode.ELEMENT_NOT_TAPPABLE,
                    "Neither 'Close' nor 'Back' button is tappable to workaround the Android system alert bug",
                )

                # tap again after close button tapped
                tap_android_asus_wifi_routers(test, False, is_wait_device_discovery)
                return
            else:
                tap_android_select_manually_button(test)

    if is_wait_device_discovery:
        # tap SSID
        Utils.delay(10)
        tap_android_ssid_text_view(test, dut.default_wifi_ssid())

        retry = 10
        for i in range(retry):
            model_name_label = qis_system_setup_page.get_model_name_label()
            if model_name_label and model_name_label.is_exist():
                logger.info("Device discovery completed")
                break
            logger.debug(f"Waiting for device discovery... (attempt {i+1}/{retry})")
            Utils.delay(3)
        else:
            logger.warn("Device discovery may not have completed after waiting")


def is_android_app_permissions_alert_exist(test: TestBase) -> bool:
    app_permissions_ok_button = get_android_app_permissions_ok_button()
    return app_permissions_ok_button.is_exist()


def tap_android_app_permissions_ok_button(test: TestBase):
    app_permissions_ok_button = get_android_app_permissions_ok_button()

    test.check(
        app_permissions_ok_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "App permissions OK button not found",
    )

    test.check(
        app_permissions_ok_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "App permissions OK button not tappable",
    )

    logger.info("Tapped 'App permissions OK' button")


def tap_android_location_permission_system_alert_allow_button(test: TestBase):
    location_permission_system_alert = SystemAlert()

    if location_permission_system_alert.is_exist():
        try:
            location_permission_system_alert.tap_allow()
            logger.info("Tapped Location Permission system alert 'Allow' button")
        except Exception as e:
            logger.info(
                f"Tap Location Permission system alert 'Allow' button failed, maybe it's already handled: {e}"
            )
    else:
        logger.info(
            "Location Permission system alert not found, maybe it's already handled"
        )


def tap_android_select_manually_button(test: TestBase):
    select_manually_button = get_android_select_manually_button()

    if select_manually_button.is_exist():
        test.check(
            select_manually_button.tap(),
            ResultCode.ELEMENT_NOT_TAPPABLE,
            "Select Manually button not tappable",
        )
        logger.info("Tapped 'Select Manually' button")


def tap_android_ssid_text_view(test: TestBase, ssid: str):
    ssid_text_view = get_android_ssid_text_view(ssid)

    test.check(
        ssid_text_view.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        f'SSID "{ssid}" text view not found',
    )

    test.check(
        ssid_text_view.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        f'SSID "{ssid}" text view not tappable',
    )

    logger.info(f'Tapped SSID "{ssid}" text view')
