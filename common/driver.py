# driver.py

"""
Driver utility for Appium tests.
"""

from appium import webdriver
from appium.options.common.base import AppiumOptions

from .logger import logger
from .app import App

APPIUM_SERVER = "http://127.0.0.1:4723"

# ios
IOS_DEVICE_UDID = "00008120-000125DE145BC01E"
IOS_BUNDLE_ID = "com.asus.asusrouter"

# android
ANDROID_DEVICE_UDID = "ce031713353b7ce60c"
ANDROID_APP_PACKAGE = "com.asus.aihome"
ANDROID_APP_WAIT_ACTIVITY = "launch.LaunchMainActivity,.MainActivity"


def get_web_driver(appium_server, desired_caps):
    options = AppiumOptions()
    options.load_capabilities(desired_caps)

    # logger.debug(f"Desired Capabilities: {desired_caps}")

    return webdriver.Remote(appium_server, options=options)


def get_ios_web_driver(
    appium_server=APPIUM_SERVER,
    platform_name="iOS",
    device_name="iPhone",
    udid=IOS_DEVICE_UDID,
    app_id=IOS_BUNDLE_ID,
    app_path=None,
):
    desired_caps = {}
    desired_caps["platformName"] = platform_name
    desired_caps["deviceName"] = device_name
    desired_caps["automationName"] = "XCUITest"
    desired_caps["newCommandTimeout"] = 3600
    desired_caps["udid"] = udid

    if app_path:
        desired_caps["app"] = app_path

    return get_web_driver(appium_server, desired_caps)


def get_ios_web_driver_from_app(app: App):
    return get_ios_web_driver(
        appium_server=app.appium_server,
        platform_name=app.platform_name,
        device_name=app.device_name,
        udid=app.udid,
        app_id=app.app_id,
        app_path=app.app_path,
    )


def get_android_web_driver(
    appium_server=APPIUM_SERVER,
    platform_name="Android",
    device_name="Android Device",
    udid=ANDROID_DEVICE_UDID,
    app_package=ANDROID_APP_PACKAGE,
    app_path=None,
    app_wait_activity=ANDROID_APP_WAIT_ACTIVITY,
):
    desired_caps = {}
    desired_caps["platformName"] = platform_name
    desired_caps["deviceName"] = device_name
    desired_caps["automationName"] = "UiAutomator2"
    desired_caps["newCommandTimeout"] = 3600
    desired_caps["udid"] = udid
    desired_caps["appPackage"] = app_package
    desired_caps["appWaitActivity"] = app_wait_activity

    if app_path:
        desired_caps["app"] = app_path

    return get_web_driver(appium_server, desired_caps)


def get_android_web_driver_from_app(app: App):
    return get_android_web_driver(
        appium_server=app.appium_server,
        platform_name=app.platform_name,
        device_name=app.device_name,
        udid=app.udid,
        app_package=app.app_id,
        app_path=app.app_path,
        app_wait_activity=ANDROID_APP_WAIT_ACTIVITY,
    )


class Driver:
    is_ios = False
    is_android = False

    def __init__(self):
        self.web_driver = None

    def set_web_driver(self, app: App):
        if app.is_ios():
            self.is_ios = True
            self.web_driver = get_ios_web_driver_from_app(app)
        elif app.is_android():
            self.is_android = True
            self.web_driver = get_android_web_driver_from_app(app)
        else:
            raise ValueError(f"Unsupported platform: {app.platform_name}")

    def is_exist(self) -> bool:
        return self.web_driver is not None

    def quit(self):
        if self.is_exist():
            self.web_driver.quit()
            self.web_driver = None

    def save_screenshot(self, *, filename=None, filepath=None) -> bool:
        if self.is_exist():
            if filepath is not None:
                self.web_driver.save_screenshot(filepath)
            elif filename is not None:
                self.web_driver.save_screenshot(filename)
            else:
                return False
            return True
        return False

    def window_size(self):
        try:
            if self.is_exist():
                size = self.web_driver.get_window_size()
                return size
            else:
                return {"width": 0, "height": 0}
        except Exception as e:
            return {"width": 0, "height": 0}

    def window_width(self):
        size = self.window_size()
        return size.get("width", 0)

    def window_height(self):
        size = self.window_size()
        return size.get("height", 0)

    def window_center_x(self):
        return self.window_width() // 2

    def window_center_y(self):
        return self.window_height() // 2

    def swipe(self, x1, y1, x2, y2, duration=500):
        if self.is_exist():
            self.web_driver.swipe(x1, y1, x2, y2, duration)


# Singleton
driver = Driver()
