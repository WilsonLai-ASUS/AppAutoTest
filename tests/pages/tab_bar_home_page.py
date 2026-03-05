"""tab bar home page"""

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
    ElementAlert,
)


def get_save_password_not_now_button() -> Element:
    return Element(ios_name="Not Now")


def get_notification_element_alert() -> ElementAlert:
    if app.is_ios():
        alert = ElementAlert(ios_name="Notification")
        return alert if alert.is_exist() else None

    # Android: standard dialog with message + Enable/Cancel.
    alert = ElementAlert(
        android_id=None,
        android_xpath=(
            "//*[@resource-id='android:id/parentPanel' "
            "and .//*[@resource-id='android:id/message'] "
            "and .//*[@resource-id='android:id/button1']]"
        ),
    )
    return alert if alert.is_exist() else None


def get_notification_system_alert() -> SystemAlert:
    system_alert = SystemAlert()
    return system_alert if system_alert.is_exist() else None


def get_account_binding_skip_button() -> Element:
    return Element(
        ios_class_chain='**/XCUIElementTypeButton[`name == "Skip"`]',
        ios_predicate_string='name == "Skip" AND label == "Skip" AND type == "XCUIElementTypeButton"',
        ios_xpath='//XCUIElementTypeButton[@name="Skip"]',
        android_id="com.asus.aihome:id/skip",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/skip"]',
    )


def get_tab_bar_settings_button() -> Element:
    return Element(
        ios_name="Settings",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/tab_text" and @text="Settings"]',
    )


def tap_first_enter_home_page_alerts(test: TestBase):
    is_checked_save_password_not_now_button = False
    is_checked_notification_alert_enable_button = False
    is_checked_notification_system_alert_allow_button = False
    is_checked_account_binding_skip_button = False

    Utils.delay(2)
    
    if app.is_android():
        # for android, just check and tap notification alert if exist
        is_checked_save_password_not_now_button = True
        is_checked_notification_system_alert_allow_button = True

    while True:
        if not is_checked_save_password_not_now_button:
            is_checked_save_password_not_now_button = True
            if tap_save_password_not_now_button(test):
                Utils.delay(2)
        elif not is_checked_notification_alert_enable_button:
            is_checked_notification_alert_enable_button = True
            if tap_notification_alert_enable_button(test):
                Utils.delay(2)
        elif not is_checked_notification_system_alert_allow_button:
            is_checked_notification_system_alert_allow_button = True
            is_checked_notification_alert_enable_button = False  # reset
            if tap_notification_system_alert_allow_button(test):
                Utils.delay(2)
        elif not is_checked_account_binding_skip_button:
            is_checked_account_binding_skip_button = True
            if tap_account_binding_skip_button(test):
                Utils.delay(2)
        else:
            break


def tap_save_password_not_now_button(test: TestBase) -> bool:
    result = False
    try:
        # find save password not now button
        save_password_not_now_button = get_save_password_not_now_button()

        if save_password_not_now_button.is_exist():
            if save_password_not_now_button.tap():
                logger.info("Tapped Save Password Not Now button")
                result = True
            else:
                logger.info("Save Password Not Now button not tappable")
        else:
            logger.info(
                "Save Password Not Now button not found, maybe it's already handled"
            )
    except Exception as e:
        logger.info(
            f"Tap Save Password Not Now button failed, maybe it's already handled: {e}"
        )
    finally:
        pass

    return result


def tap_notification_alert_enable_button(test: TestBase) -> bool:
    result = False
    try:
        # find notification element alert
        notification_element_alert = get_notification_element_alert()

        if notification_element_alert is not None:
            if notification_element_alert.tap("Enable"):
                logger.info("Tapped Notification alert Enable button")
                result = True
            else:
                logger.info("Notification alert Enable button not tappable")
        else:
            logger.info(
                "Notification alert Enable button not found, maybe it's already handled"
            )
    except Exception as e:
        logger.info(
            f"Tap Notification alert Enable button failed, maybe it's already handled: {e}"
        )
    finally:
        pass

    return result


def tap_notification_system_alert_allow_button(test: TestBase) -> bool:
    result = False
    try:
        # find notification system alert
        notification_system_alert = get_notification_system_alert()

        if notification_system_alert is not None:
            if notification_system_alert.tap_allow():
                logger.info("Tapped Notification system alert Allow button")
                result = True
            else:
                logger.info("Notification system alert Allow button not tappable")
        else:
            logger.info(
                "Notification system alert not found, maybe it's already handled"
            )
    except Exception as e:
        logger.info(
            f"Tap Notification system alert Allow button failed, maybe it's already handled: {e}"
        )
    finally:
        pass

    return result


def tap_account_binding_skip_button(test: TestBase) -> bool:
    result = False
    try:
        # find account binding skip button
        account_binding_skip_button = get_account_binding_skip_button()

        if account_binding_skip_button.is_exist():
            if account_binding_skip_button.tap():
                logger.info("Tapped Account Binding Skip button")
                result = True
            else:
                logger.info("Account Binding Skip button not tappable")
        else:
            logger.info(
                "Account Binding Skip button not found, maybe it's already handled"
            )
    except Exception as e:
        logger.info(
            f"Tap Account Binding Skip button failed, maybe it's already handled: {e}"
        )
    finally:
        pass


def tap_tab_bar_settings_button(test: TestBase) -> bool:
    # find tab bar settings button
    tab_bar_settings_button = get_tab_bar_settings_button()

    test.check(
        tab_bar_settings_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Tab Bar Settings button not found",
    )

    test.check(
        tab_bar_settings_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Tab Bar Settings button not tappable",
    )

    logger.info("Tapped Tab Bar 'Settings' button")
