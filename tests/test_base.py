# test_base.py

"""
TestBase
"""

import sys
import os
import inspect
import argparse

from common import (
    app,
    logger,
    driver,
    dut,
    screenshot,
    Utils,
    Element,
    ElementAlert,
    ElementFinder,
    SystemAlert,
    Result,
    ResultCode,
)


class TestBase:
    def __init__(self, argvs):

        # read config path from argvs
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-app",
            "--app-config",
            default="config/ios_config.json",
            help="App config file path",
        )
        parser.add_argument(
            "-dut", "--dut-config", default=None, help="DUT config file path"
        )
        args = parser.parse_args()

        app_config_path = args.app_config
        dut_config_path = args.dut_config

        app.load(app_config_path)
        dut.load(dut_config_path)
        logger.debug(f"Config loaded: {app.__dict__}")

    # ====================================================
    # Setup 和 Teardown
    # ====================================================

    def setup(self):
        """setup"""
        logger.info("Setting up test...")

        try:
            # logger
            logger.set_path(app.log_path)
            logger.set_level(app.log_level)

            # screenshot
            screenshot.set_dir(app.screenshot_dir)

            # driver
            driver.set_web_driver(app)

            if not driver.is_exist:
                raise RuntimeError("Failed to initialize driver")

            logger.info("Driver initialized successfully")

            # delay to ensure app is stable
            Utils.delay()
        except Exception as e:
            logger.error("Exception occurred while initializing driver: %s", str(e))
            raise

    def teardown(self):
        """teardown"""
        if driver.is_exist():
            logger.info("Tearing down test...")
            driver.quit()
            logger.info("Driver closed")

    def run_test(self, test_func) -> Result:
        """run test_func with setup and teardown, and handle exceptions"""
        try:
            self.setup()

            # test privacy policy flow before running
            self.test_asus_privacy_policy_flow()

            test_func()
            return Result(ResultCode.SUCCESS, "Test passed")
        except Result as r:
            logger.error("Test failed with error: %s", r.description())
            screenshot.take(f"{test_func.__name__}_FAILURE")
            return r
        except Exception as e:
            logger.error("Test failed with exception: %s", str(e))
            screenshot.take(f"{test_func.__name__}_FAILURE")
            return Result(ResultCode.FAILURE, str(e))
        finally:
            self.teardown()

    def test(self):
        """test entry point, to be overridden by subclasses"""
        pass

    def check(self, condition: bool, code: ResultCode, message: str):
        """check condition and return Result"""
        if not condition:
            raise Result(code, message)

    def finish(self, result: Result, test_name=None):
        """log result and return Result"""
        if test_name is None:
            # get the caller's filename
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            # get the filename without path and .py
            test_name = os.path.splitext(os.path.basename(filename))[0]

        if result.code == ResultCode.SUCCESS:
            logger.passed(test_name)
        else:
            logger.failed(f"{test_name}: {result.description}")

        exit(result.code.value)

    # ==========================================================================
    # Privacy Policy
    # ==========================================================================

    def test_asus_privacy_policy_flow(self):
        """test EULA and Privacy Policy flow"""

        # prevent last test case failure due to system permission alert by handling the alert first, if exists
        if app.is_ios():
            self.test_system_permission_alert()
            
        self.test_asus_eula()
        self.test_asus_privacy_policy()

        if app.is_ios():
            Utils.delay(2)
            self.test_system_permission_alert()

        Utils.delay(4)

    def test_asus_eula(self):
        """test EULA flow"""

        # find title bar
        title_bar = ElementFinder.AsusEulaPage.get_title_bar()

        # not on eula page, skip the test and return success
        if not title_bar.is_exist():
            logger.info("Not on EULA page, skipping EULA test")
            return

        # find asus eula scroll view
        asus_eula_scroll_view = ElementFinder.AsusEulaPage.get_scroll_view()

        self.check(
            asus_eula_scroll_view.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "EULA scroll view not found",
        )

        # swipe 2 times to scroll to the bottom
        for _ in range(2):
            self.swipe_up(element=asus_eula_scroll_view, duration=50)

        is_above_16_button_tapped = False

        # try to find and tap the "Above 16 years" button, if not found, swipe up and try again, repeat for 3 times
        for _ in range(3):
            above_16_button = ElementFinder.AsusEulaPage.get_above_16_button()
            if above_16_button.is_exist():
                self.check(
                    above_16_button.tap(),
                    ResultCode.ELEMENT_NOT_TAPPABLE,
                    "Above 16 years button not tappable",
                )

                logger.info("Tapped 'Above 16 years' button on EULA page successfully")
                is_above_16_button_tapped = True
                break
            else:
                logger.debug(
                    "Above 16 years button not found, swiping up to find the button..."
                )

            # try to swipe up to find the agree button or other elements
            self.swipe_up(element=asus_eula_scroll_view, duration=50)

        self.check(
            is_above_16_button_tapped,
            ResultCode.ELEMENT_NOT_FOUND,
            "Above 16 years button not found after swiping",
        )

        asus_eula_agree_button = ElementFinder.AsusEulaPage.get_agree_button()

        self.check(
            asus_eula_agree_button.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "Agree button not found",
        )

        self.check(
            asus_eula_agree_button.is_enabled(),
            ResultCode.ELEMENT_NOT_TAPPABLE,
            "Agree button not enabled",
        )

        self.check(
            asus_eula_agree_button.tap(),
            ResultCode.ELEMENT_NOT_TAPPABLE,
            "Agree button not tappable",
        )

        logger.info("Agreed to EULA successfully")

    def test_asus_privacy_policy(self):
        """test privacy policy flow"""

        # find title bar
        title_bar = ElementFinder.AsusPrivacyPolicyPage.get_title_bar()

        # not on privacy policy page, skip the test and return success
        if not title_bar.is_exist():
            logger.info("Not on Privacy Policy page, skipping Privacy Policy test")
            return

        # find asus pp scroll view
        asus_pp_scroll_view = ElementFinder.AsusPrivacyPolicyPage.get_scroll_view()

        self.check(
            asus_pp_scroll_view.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "Privacy Policy scroll view not found",
        )

        # swipe 1 time
        self.swipe_up(element=asus_pp_scroll_view, duration=50)

        # find agree button
        agree_button = ElementFinder.AsusPrivacyPolicyPage.get_agree_button()

        self.check(
            agree_button.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "Privacy Policy Agree button not found",
        )

        self.check(
            agree_button.is_enabled(),
            ResultCode.ELEMENT_NOT_TAPPABLE,
            "Privacy Policy Agree button not enabled",
        )

        self.check(
            agree_button.tap(),
            ResultCode.ELEMENT_NOT_TAPPABLE,
            "Privacy Policy Agree button not tappable",
        )

        logger.info("Agreed to Privacy Policy successfully")

    # ==========================================================================
    # Alert
    # ==========================================================================

    def test_system_permission_alert(self):
        while True:
            alert = SystemAlert()

            if alert.is_exist():
                logger.info(
                    f"Alert title: {alert.title()}, body: {alert.text()}, buttons: {alert.buttons()}"
                )

                if alert.tap_allow():
                    logger.info("Tapped 'Allow' on location permission alert")
                elif alert.tap_allow_while_using_app():
                    logger.info(
                        "Tapped 'Allow While Using App' on location permission alert"
                    )
                else:
                    logger.error(
                        "Location permission alert detected but no expected buttons found"
                    )
                    break

                Utils.delay()
            else:
                logger.info("No system alert detected")
                return

    def test_upgrade_alert(self):
        while True:
            alert = SystemAlert()

            if alert.is_exist():
                logger.info(
                    f"Alert title: {alert.title()}, body: {alert.text()}, buttons: {alert.buttons()}"
                )

                if alert.tap("Update"):
                    logger.info("Tapped 'Update' on upgrade alert")
                else:
                    logger.error("Upgrade alert detected but 'Update' button not found")
                    break

                Utils.delay()
            else:
                logger.info("No upgrade alert detected")
                return

    def test_upgrade_alert2(self):
        while True:
            # alert = ElementAlert(ios_predicate_string='name == "Notice" AND label == "Notice" AND type == "XCUIElementTypeAlert"')
            alert = ElementAlert()

            if alert.is_exist():
                logger.info(
                    f"Alert title: {alert.title()}, body: {alert.body()}, buttons: {alert.buttons()}"
                )

                if alert.tap("Update"):
                    logger.info("Tapped 'Update' on upgrade alert")
                else:
                    logger.error("Upgrade alert detected but 'Update' button not found")
                    break

                Utils.delay()
            else:
                logger.info("No upgrade alert detected")
                return

    # ==========================================================================
    # Swipe
    # ==========================================================================

    def swipe(self, x1, y1, x2, y2, duration=500):
        logger.debug(
            f"Swiping from ({x1}, {y1}) to ({x2}, {y2}) with duration {duration}ms"
        )
        try:
            driver.swipe(x1, y1, x2, y2, duration)
            Utils.delay(0.5)
        except Exception as e:
            logger.error(f"Error during swipe: {e}")

    def swipe_up(
        self,
        *,
        element=None,
        progress={"begin": 0.0, "end": 1.0},
        duration=500,
    ):
        """向上滑動"""
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        begin_progress = progress.get("begin", 0.0)
        end_progress = progress.get("end", 1.0)

        if element is not None and element.is_exist():
            x1 = element.x() + element.center_x()
            y1 = element.y() + int(element.height() * (1 - begin_progress)) - 1
            x2 = x1
            y2 = element.y() + int(element.height() * (1 - end_progress))
        else:
            x1 = driver.window_center_x()
            y1 = int(driver.window_height() * (1 - begin_progress))
            x2 = x1
            y2 = int(driver.window_height() * (1 - end_progress))

        self.swipe(x1, y1, x2, y2, duration)

    def swipe_down(
        self,
        *,
        element=None,
        progress={"begin": 0.0, "end": 1.0},
        duration=500,
    ):
        """向下滑動"""
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        begin_progress = progress.get("begin", 0.0)
        end_progress = progress.get("end", 1.0)

        if element is not None and element.is_exist():
            x1 = element.x() + element.center_x()
            y1 = element.y() + int(element.height() * begin_progress) + 1
            x2 = x1
            y2 = element.y() + int(element.height() * end_progress)
        else:
            x1 = driver.window_center_x()
            y1 = int(driver.window_height() * begin_progress)
            x2 = x1
            y2 = int(driver.window_height() * end_progress)

        self.swipe(x1, y1, x2, y2, duration)

    def swipe_left(
        self, *, element=None, progress={"begin": 0.0, "end": 1.0}, duration=500
    ):
        """向左滑動"""
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        begin_progress = progress.get("begin", 0.0)
        end_progress = progress.get("end", 1.0)

        if element is not None and element.is_exist():
            x1 = element.x() + int(element.width() * (1 - begin_progress)) - 1
            y1 = element.y() + element.center_y()
            x2 = element.x() + int(element.width() * (1 - end_progress))
            y2 = y1
        else:
            x1 = int(driver.window_width() * (1 - begin_progress))
            y1 = driver.window_center_y()
            x2 = int(driver.window_width() * (1 - end_progress))
            y2 = y1

        self.swipe(x1, y1, x2, y2, duration)

    def swipe_right(
        self, *, element=None, progress={"begin": 0.0, "end": 1.0}, duration=500
    ):
        """向右滑動"""
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        begin_progress = progress.get("begin", 0.0)
        end_progress = progress.get("end", 1.0)

        if element is not None and element.is_exist():
            x1 = element.x() + int(element.width() * begin_progress) + 1
            y1 = element.y() + element.center_y()
            x2 = element.x() + int(element.width() * end_progress)
            y2 = y1
        else:
            x1 = int(driver.window_width() * begin_progress)
            y1 = driver.window_center_y()
            x2 = int(driver.window_width() * end_progress)
            y2 = y1

        self.swipe(x1, y1, x2, y2, duration)


if __name__ == "__main__":
    test = TestBase(sys.argv)
    test.finish(test.test())
