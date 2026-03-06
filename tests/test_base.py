# test_base.py

"""
TestBase
"""

import sys
import os
import inspect
import argparse
from dataclasses import dataclass
from datetime import datetime

from common import (
    app,
    logger,
    driver,
    dut,
    record,
    Utils,
    Element,
    ElementAlert,
    ElementFinder,
    SystemAlert,
    Result,
    ResultCode,
)


@dataclass(frozen=True, slots=True)
class RunOptions:
    do_setup: bool = True
    do_teardown: bool = True
    run_privacy_flow: bool = True


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
        argvs = argvs or sys.argv
        args = parser.parse_args(argvs[1:])

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
            # Create per-run results directory structure:
            base_results_dir = app.results_dir()
            if not base_results_dir:
                base_results_dir = Utils.get_absolute_path("results")

            run_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            run_dir = os.path.join(base_results_dir, run_ts)
            logs_dir = os.path.join(run_dir, "logs")
            screenshots_dir = os.path.join(run_dir, "screenshots")
            videos_dir = os.path.join(run_dir, "videos")
            reports_dir = os.path.join(run_dir, "reports")

            os.makedirs(logs_dir, exist_ok=True)
            os.makedirs(screenshots_dir, exist_ok=True)
            os.makedirs(videos_dir, exist_ok=True)
            os.makedirs(reports_dir, exist_ok=True)

            # logger
            logger.set_path(os.path.join(logs_dir, "test.log"))
            logger.set_level(app.log_level())

            # record
            record.set_dirs(screenshots_dir=screenshots_dir, videos_dir=videos_dir)

            # driver
            driver.set_web_driver(app)

            if not driver.is_exist():
                raise RuntimeError("Failed to initialize driver")

            logger.info("Driver initialized successfully")

            # start recording
            record.start_recording()

            # delay to ensure app is stable
            Utils.delay()
        except Exception as e:
            logger.error("Exception occurred while initializing driver: %s", str(e))
            raise

    def teardown(self):
        """teardown"""
        logger.info("Tearing down test...")

        # stop recording
        record.stop_recording()

        if app.app_terminate:
            if driver.is_exist():
                logger.info("Terminating app...")
                driver.quit()
                logger.info("App terminated")
            else:
                logger.warn("Driver does not exist during teardown, skipping quit()")
        else:
            logger.info(
                "App termination disabled, skipping driver.quit() in teardown()"
            )

    def run_test(
        self,
        test_func,
        *,
        options: RunOptions | None = None,
    ) -> Result:
        """run test_func and handle exceptions.

        By default, this method manages the full lifecycle (setup -> optional flows -> test -> teardown).
        For suite-style execution, you can disable setup/teardown to reuse the same driver/session.
        """
        options = options or RunOptions()

        if not options.do_setup and not driver.is_exist():
            return Result(
                ResultCode.FAILURE,
                "Driver is not initialized. Run the first test with do_setup=True, or call setup() once before suite execution.",
            )
        try:
            if options.do_setup:
                self.setup()

            if options.run_privacy_flow:
                self.test_asus_privacy_policy_flow()

            test_func()
            return Result(ResultCode.SUCCESS, "Test passed")
        except Result as r:
            logger.error("Test failed with error: %s", r.description())
            record.screenshot(f"{test_func.__name__}_FAILURE")
            return r
        except Exception as e:
            logger.error("Test failed with exception: %s", str(e))
            record.screenshot(f"{test_func.__name__}_FAILURE")
            return Result(ResultCode.FAILURE, str(e))
        finally:
            if options.do_teardown:
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
            logger.fail(f"{test_name}: {result.description()}")

        exit(result.code.value)

    # ==========================================================================
    # Privacy Policy
    # ==========================================================================

    def test_asus_privacy_policy_flow(self):
        """test EULA and Privacy Policy flow"""

        # prevent last test case failure due to system permission alert by handling the alert first, if exists
        if app.is_ios():
            self.test_ios_system_permission_alert()

        self.test_asus_eula()
        self.test_asus_privacy_policy()

        if app.is_ios():
            Utils.delay(2)
            self.test_ios_system_permission_alert()

        Utils.delay(4)

    def test_asus_eula(self):
        """test EULA flow"""

        # find title bar
        title_bar = ElementFinder.AsusEulaPage.get_title_bar()

        if title_bar.is_exist("End User License Agreement") == False:
            logger.info("Not on EULA page, skipping EULA test")
            return

        # find asus eula scroll view
        asus_eula_scroll_view = ElementFinder.AsusEulaPage.get_scroll_view()

        self.check(
            asus_eula_scroll_view.is_exist(),
            ResultCode.ELEMENT_NOT_FOUND,
            "EULA scroll view not found",
        )

        # swipe 1 time to scroll to the bottom
        self.swipe_up(element=asus_eula_scroll_view, duration=0.02)

        is_above_16_button_tapped = False

        # try to find and tap the "Above 16 years" button, if not found, swipe up and try again, repeat for 3 times
        retry_count = 3
        if app.is_android():
            retry_count += 7

        for i in range(retry_count):
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
                # print retry count
                logger.debug(
                    f"Above 16 years button not found, swiping up to find the button... (attempt {i+1}/{retry_count})"
                )

            # try to swipe up to find the agree button or other elements
            self.swipe_up(element=asus_eula_scroll_view, duration=0.02)

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
        if app.is_ios():
            if title_bar.is_exist("ASUS PRIVACY NOTICE") == False:
                logger.info("Not on Privacy Policy page, skipping Privacy Policy test")
                return
        else:
            if (
                title_bar.is_exist("ASUS Privacy Notice / ASUS EU Data Act Notice")
                == False
            ):
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
        self.swipe_up(element=asus_pp_scroll_view, duration=0.02)

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

    def test_ios_system_permission_alert(self):
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

    # ==========================================================================
    # Swipe
    # ==========================================================================

    def swipe_up(
        self,
        *,
        element: Element | None = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向上滑動"""
        if element is not None and element.is_exist():
            rect = element.rect()
            rect["height"] -= 1
            driver.swipe_up(
                rect=rect,
                progress=progress,
                duration=duration,
                delay_after=delay_after,
            )
        else:
            driver.swipe_up(
                progress=progress, duration=duration, delay_after=delay_after
            )

    def swipe_down(
        self,
        *,
        element: Element | None = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向下滑動"""
        if element is not None and element.is_exist():
            rect = element.rect()
            rect["y"] += 1
            rect["height"] -= 1
            driver.swipe_down(
                rect=rect,
                progress=progress,
                duration=duration,
                delay_after=delay_after,
            )
        else:
            driver.swipe_down(
                progress=progress, duration=duration, delay_after=delay_after
            )

    def swipe_left(
        self,
        *,
        element: Element | None = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向左滑動"""
        if element is not None and element.is_exist():
            rect = element.rect()
            rect["width"] -= 1
            driver.swipe_left(
                rect=rect,
                progress=progress,
                duration=duration,
                delay_after=delay_after,
            )
        else:
            driver.swipe_left(
                progress=progress, duration=duration, delay_after=delay_after
            )

    def swipe_right(
        self,
        *,
        element: Element | None = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向右滑動"""
        if element is not None and element.is_exist():
            rect = element.rect()
            rect["x"] += 1
            rect["width"] -= 1
            driver.swipe_right(
                rect=rect,
                progress=progress,
                duration=duration,
                delay_after=delay_after,
            )
        else:
            driver.swipe_right(
                progress=progress, duration=duration, delay_after=delay_after
            )

    def connect_wifi(self, ssid, password=None):
        driver.connect_wifi(ssid, password)


def main(argv=None):
    test = TestBase(argv or sys.argv)
    test.finish(test.test())


if __name__ == "__main__":
    main()
