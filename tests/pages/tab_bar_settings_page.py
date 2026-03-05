"""tab bar settings page"""

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


def get_tab_bar_settings_button() -> Element:
    return Element(
        ios_name="Settings",
        android_xpath='//android.widget.TextView[@resource-id="com.asus.aihome:id/tab_text" and @text="Settings"]',
    )


def get_feature_label(feature_name) -> Element:
    return Element(
        ios_static_text_name=feature_name,
        android_xpath=f'//android.widget.TextView[@resource-id="com.asus.aihome:id/title" and @text="{feature_name}"]',
    )


def get_scroll_view() -> Element:
    return Element(
        ios_class_chain="**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable",
        ios_predicate_string='type == "XCUIElementTypeTable"',
        ios_xpath="//XCUIElementTypeTable",
        android_id="com.asus.aihome:id/container",
        android_xpath='//android.widget.FrameLayout[@resource-id="com.asus.aihome:id/container"]',
    )


def get_factory_default_slider() -> Element:
    return Element(
        ios_class_chain='**/XCUIElementTypeSlider[`value == "0%"`]',
        ios_predicate_string='value == "0%" AND type == "XCUIElementTypeSlider"',
        ios_xpath='//XCUIElementTypeSlider[@value="0%"]',
        android_id="com.asus.aihome:id/slideToActView",
        android_xpath='//android.view.View[@resource-id="com.asus.aihome:id/slideToActView"]',
    )


def tap_tab_bar_settings_button(test: TestBase):
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


def tap_feature_label(test: TestBase, feature_name):
    # scroll to top first
    scroll_view = get_scroll_view()

    test.check(
        scroll_view.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Scroll view not found",
    )

    logger.debug("scroll view rect: " + str(scroll_view.rect()))

    test.swipe_down(
        element=scroll_view, progress={"begin": 0.2, "end": 1}, duration=0.05
    )

    # find feature label
    retry_count = 2

    for i in range(retry_count):
        feature_label = get_feature_label(feature_name)

        if feature_label.is_exist():
            test.check(
                feature_label.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                f"{feature_name} label not tappable",
            )
            logger.info(f"Tapped '{feature_name}' label")
            return
        else:
            # swipe up to find the element
            if i < retry_count - 1:
                test.swipe_up(
                    element=scroll_view, progress={"begin": 0.2, "end": 1}, duration=2
                )

    test.check(False, ResultCode.ELEMENT_NOT_FOUND, f"{feature_name} label not found")


def confirm_factory_default(test: TestBase):
    # find factory default confirm slider
    factory_default_slider = get_factory_default_slider()

    test.check(
        factory_default_slider.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Factory Default confirm slider not found",
    )

    test.swipe_right(
        element=factory_default_slider,
        progress={"begin": 0, "end": 1},
        duration=1,
        delay_after=15,
    )

    logger.info("Swiped right on Factory Default confirm slider")

    if app.is_ios():
        applying_alert = ElementAlert(ios_name="Notice")

        test.check(
            applying_alert.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "Applying alert not found after confirming factory default",
        )

        test.check(
            applying_alert.body() == "Apply settings successfully.",
            ResultCode.ELEMENT_NOT_FOUND,
            "Applying alert body is not 'Apply settings successfully.'",
        )

        test.check(
            applying_alert.buttons() == ["OK"],
            ResultCode.ELEMENT_NOT_FOUND,
            "OK button not found in Applying alert",
        )
