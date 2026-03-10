# driver.py

"""
Driver utility for Appium tests.
"""

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .logger import logger
from .app import App, app
from .utils import Utils

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

    """
    noReset | fullReset | What happens to app state when session ends:
    ---------------------------------------------------------------
    FALSE   | FALSE     | Installs app if no present, keeps data bewteen sessions.
    TRUE    | FALSE     | Uninstalls > Reinstalls > Resets app state (redundant, slow).
    FALSE   | TRUE      | Assumes app installed, keeps data (fast but risky).
    TRUE    | TRUE      | Conflicting: noReset wins, fullReset ignored.
    """
    return webdriver.Remote(appium_server, options=options)


def get_desired_caps(
    platform_name,
    device_name,
    automationName,
    newCommandTimeout,
    udid,
    app_path,
    app_reinstall,
    app_launch,
    app_terminate,
):
    desired_caps = {}
    desired_caps["platformName"] = platform_name
    desired_caps["deviceName"] = device_name
    desired_caps["automationName"] = automationName
    desired_caps["newCommandTimeout"] = newCommandTimeout
    desired_caps["udid"] = udid

    if app_path:
        desired_caps["app"] = app_path

    if app_reinstall:
        if not app_path:
            logger.error("App path is required when app_reinstall is False")
            raise ValueError("App path is required when app_reinstall is False")
    else:
        desired_caps["noReset"] = True
        desired_caps["fullReset"] = False

    desired_caps["forceAppLaunch"] = app_launch
    desired_caps["shouldTerminateApp"] = app_terminate

    return desired_caps


def get_ios_web_driver(
    appium_server=APPIUM_SERVER,
    platform_name="iOS",
    device_name="iPhone",
    udid=IOS_DEVICE_UDID,
    app_id=IOS_BUNDLE_ID,
    app_path=None,
    app_reinstall=True,
    app_launch=True,
    app_terminate=True,
):
    desired_caps = get_desired_caps(
        platform_name=platform_name,
        device_name=device_name,
        automationName="XCUITest",
        newCommandTimeout=3600,
        udid=udid,
        app_path=app_path,
        app_reinstall=app_reinstall,
        app_launch=app_launch,
        app_terminate=app_terminate,
    )

    # ios specific capabilities
    desired_caps["bundleId"] = app_id

    return get_web_driver(appium_server, desired_caps)


def get_android_web_driver(
    appium_server=APPIUM_SERVER,
    platform_name="Android",
    device_name="Android Device",
    udid=ANDROID_DEVICE_UDID,
    app_package=ANDROID_APP_PACKAGE,
    app_path=None,
    app_wait_activity=ANDROID_APP_WAIT_ACTIVITY,
    app_reinstall=True,
    app_launch=True,
    app_terminate=True,
):
    desired_caps = get_desired_caps(
        platform_name=platform_name,
        device_name=device_name,
        automationName="UiAutomator2",
        newCommandTimeout=3600,
        udid=udid,
        app_path=app_path,
        app_reinstall=app_reinstall,
        app_launch=app_launch,
        app_terminate=app_terminate,
    )

    # android specific capabilities
    desired_caps["appPackage"] = app_package
    desired_caps["appWaitActivity"] = app_wait_activity

    return get_web_driver(appium_server, desired_caps)


def get_ios_web_driver_from_app(app: App):
    return get_ios_web_driver(
        appium_server=app.appium_server(),
        platform_name=app.platform_name(),
        device_name=app.device_name(),
        udid=app.udid(),
        app_id=app.app_id(),
        app_path=app.app_path(),
        app_reinstall=app.app_reinstall(),
        app_launch=app.app_launch(),
        app_terminate=app.app_terminate(),
    )


def get_android_web_driver_from_app(app: App):
    return get_android_web_driver(
        appium_server=app.appium_server(),
        platform_name=app.platform_name(),
        device_name=app.device_name(),
        udid=app.udid(),
        app_package=app.app_id(),
        app_path=app.app_path(),
        app_wait_activity=ANDROID_APP_WAIT_ACTIVITY,
        app_reinstall=app.app_reinstall(),
        app_launch=app.app_launch(),
        app_terminate=app.app_terminate(),
    )


class Driver:
    web_driver = None

    def __init__(self):
        pass

    def set_web_driver(self, app: App):
        if app.is_ios():
            self.web_driver = get_ios_web_driver_from_app(app)
        elif app.is_android():
            self.web_driver = get_android_web_driver_from_app(app)
        else:
            raise ValueError(f"Unsupported platform: {app.platform_name}")

    def is_exist(self) -> bool:
        return self.web_driver is not None

    def quit(self):
        if self.is_exist():
            self.web_driver.quit()
            self.web_driver = None
        else:
            logger.warn("Web driver does not exist, ignoring quit()")

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

    def start_recording_screen(self, *, time_limit_s: int = 180):
        if self.is_exist():
            time_limit_s = int(time_limit_s)
            if time_limit_s <= 0:
                time_limit_s = 180
            self.web_driver.start_recording_screen(
                videoType="mpeg4",
                videoQuality="medium",
                videoSize="1280x720",
                bitRate=2000000,
                timeLimit=time_limit_s,
            )

    def stop_recording_screen(self, *, filename=None, filepath=None) -> bool:
        if self.is_exist():
            video_base64 = self.web_driver.stop_recording_screen()
            if video_base64:
                import base64

                video_data = base64.b64decode(video_base64)
                if filepath is not None:
                    with open(filepath, "wb") as f:
                        f.write(video_data)
                elif filename is not None:
                    with open(filename, "wb") as f:
                        f.write(video_data)
                else:
                    return False
                return True
            else:
                return False
        return False

    def get_elements_by_ios_predicate_string(self, predicate_string, timeout=1):
        try:
            return self.web_driver.find_elements(
                AppiumBy.IOS_PREDICATE, predicate_string
            )
        except:
            return []  # 找不到元素就回傳空 list

    def get_element_by_ios_predicate_string(self, predicate_string, timeout=1):
        elements = self.get_elements_by_ios_predicate_string(predicate_string, timeout)
        return elements[-1] if elements else None

    def get_elements_by_ios_class_chain(self, class_chain, timeout=1):
        try:
            return self.web_driver.find_elements(AppiumBy.IOS_CLASS_CHAIN, class_chain)
        except:
            return []  # 找不到元素就回傳空 list

    def get_element_by_ios_class_chain(self, class_chain, timeout=1):
        elements = self.get_elements_by_ios_class_chain(class_chain, timeout)
        return elements[-1] if elements else None

    def get_elements_by_android_id(self, android_id, timeout=1):
        try:
            return self.web_driver.find_elements(AppiumBy.ID, android_id)
        except:
            return []  # 找不到元素就回傳空 list

    def get_element_by_android_id(self, android_id, timeout=1):
        elements = self.get_elements_by_android_id(android_id, timeout)
        return elements[-1] if elements else None

    def get_elements_by_xpath(self, xpath, timeout=1):
        wait = WebDriverWait(self.web_driver, timeout)
        try:
            elements = wait.until(
                EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath))
            )
            return elements  # list，可能有多個元素
        except:
            return []  # 找不到元素就回傳空 list

    def get_element_by_xpath(self, xpath, timeout=1):
        elements = self.get_elements_by_xpath(xpath, timeout)
        return (
            elements[-1] if elements else None
        )  # 回傳最後一個元素，如果找不到就回傳 None

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

    def swipe(self, x1, y1, x2, y2, duration=0.5, delay_after=1.0):
        if self.is_exist():
            if app.is_android() and duration < 0.2:
                # Android swipe with very short duration can be unreliable, set a minimum
                duration = 0.2

            direction_log = ""

            if x1 > x2:
                direction_log += "left"
            elif x1 < x2:
                direction_log += "right"

            if y1 > y2:
                if direction_log:
                    direction_log += "-"
                direction_log += "up"
            elif y1 < y2:
                if direction_log:
                    direction_log += "-"
                direction_log += "down"

            logger.debug(
                f"Swiping \"{direction_log}\" from ({x1}, {y1}) to ({x2}, {y2}) with duration {duration}s"
            )
            try:
                self.web_driver.swipe(x1, y1, x2, y2, duration * 1000)
            except Exception as e:
                logger.error(f"Error during swipe: {e}")

            Utils.delay(duration + delay_after)
        else:
            logger.warn("Web driver does not exist, cannot perform swipe()")

    def swipe_up(
        self,
        *,
        rect: dict = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向上滑動"""
        begin_progress = progress.get("begin", 0.2)
        end_progress = progress.get("end", 1.0)

        if rect:
            x1 = rect.get("x", 0) + rect.get("width", 0) // 2
            y1 = (
                rect.get("y", 0) + int(rect.get("height", 0) * (1 - begin_progress)) - 1
            )
            x2 = x1
            y2 = rect.get("y", 0) + int(rect.get("height", 0) * (1 - end_progress))
        else:
            x1 = self.window_center_x()
            y1 = int(self.window_height() * (1 - begin_progress))
            x2 = x1
            y2 = int(self.window_height() * (1 - end_progress))

        self.swipe(x1, y1, x2, y2, duration, delay_after)

    def swipe_down(
        self,
        *,
        rect: dict = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向下滑動"""
        begin_progress = progress.get("begin", 0.2)
        end_progress = progress.get("end", 1.0)

        if rect:
            x1 = rect.get("x", 0) + rect.get("width", 0) // 2
            y1 = rect.get("y", 0) + int(rect.get("height", 0) * begin_progress)
            x2 = x1
            y2 = rect.get("y", 0) + int(rect.get("height", 0) * end_progress)
        else:
            x1 = self.window_center_x()
            y1 = int(self.window_height() * begin_progress)
            x2 = x1
            y2 = int(self.window_height() * end_progress)

        self.swipe(x1, y1, x2, y2, duration, delay_after)

    def swipe_left(
        self,
        *,
        rect: dict = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向左滑動"""
        begin_progress = progress.get("begin", 0.2)
        end_progress = progress.get("end", 1.0)

        if rect:
            x1 = rect.get("x", 0) + int(rect.get("width", 0) * (1 - begin_progress))
            y1 = rect.get("y", 0) + rect.get("height", 0) // 2
            x2 = rect.get("x", 0) + int(rect.get("width", 0) * (1 - end_progress))
            y2 = y1
        else:
            x1 = int(self.window_width() * (1 - begin_progress))
            y1 = self.window_center_y()
            x2 = int(self.window_width() * (1 - end_progress))
            y2 = y1

        self.swipe(x1, y1, x2, y2, duration, delay_after)

    def swipe_right(
        self,
        *,
        rect: dict = None,
        progress={"begin": 0.2, "end": 1.0},
        duration=0.5,
        delay_after=1.0,
    ):
        """向右滑動"""
        begin_progress = progress.get("begin", 0.2)
        end_progress = progress.get("end", 1.0)

        if rect:
            x1 = rect.get("x", 0) + int(rect.get("width", 0) * begin_progress)
            y1 = rect.get("y", 0) + rect.get("height", 0) // 2
            x2 = rect.get("x", 0) + int(rect.get("width", 0) * end_progress)
            y2 = y1
        else:
            x1 = int(self.window_width() * begin_progress)
            y1 = self.window_center_y()
            x2 = int(self.window_width() * end_progress)
            y2 = y1

        self.swipe(x1, y1, x2, y2, duration, delay_after)

    def hide_keyboard(self) -> bool:
        if not self.is_exist():
            return False

        errors: list[str] = []

        def _try_hide(*, strategy=None, key_name=None) -> bool:
            try:
                if strategy is None and key_name is None:
                    self.web_driver.hide_keyboard()
                else:
                    self.web_driver.hide_keyboard(strategy=strategy, key_name=key_name)
                return True
            except Exception as e:
                errors.append(str(e))
                return False

        # step 1: try default hide_keyboard
        if _try_hide():
            return True

        # step 2: try different strategies for iOS
        if _try_hide(strategy="tapOutside"):
            return True

        # step 3: try pressing "Done" key for iOS
        if _try_hide(strategy="pressKey", key_name="Done"):
            return True

        # step 4: try tapping "Done" button for iOS
        if app.is_ios():
            for name in ("Done", "完成"):
                try:
                    btn = self.get_element_by_xpath(
                        f'//XCUIElementTypeButton[@name="{name}"]', timeout=1
                    )
                    if btn and btn.is_displayed():
                        btn.click()
                        return True
                except Exception as e:
                    errors.append(str(e))

        logger.warn("Failed to hide keyboard: %s", errors[-1] if errors else "unknown")
        return False

    def goto_ios_settings_app(self, delay=3):
        logger.info("Switching to iOS Settings app")
        self.web_driver.execute_script(
            "mobile: activateApp", {"bundleId": "com.apple.Preferences"}
        )
        Utils.delay(delay)

    def goto_ios_asusrouter_app(self, delay=3):
        logger.info("Switching back to ASUS Router app")
        self.web_driver.execute_script(
            "mobile: activateApp", {"bundleId": IOS_BUNDLE_ID}
        )
        Utils.delay(delay)

    def goto_android_settings_app(self, delay=3):
        if not (self.is_exist() and app.is_android()):
            return

        logger.info("Switching to Android Settings app")
        try:
            # Appium: activate app by package name
            self.web_driver.activate_app("com.android.settings")
        except Exception:
            # Fallback: start Settings main activity via shell
            try:
                self.web_driver.execute_script(
                    "mobile: shell",
                    {
                        "command": "am",
                        "args": ["start", "-a", "android.settings.SETTINGS"],
                    },
                )
            except Exception as e:
                logger.warn("Failed to open Android Settings: %s", e)
                return

        Utils.delay(delay)

    def goto_android_asusrouter_app(self, delay=3):
        if not (self.is_exist() and app.is_android()):
            return

        logger.info("Switching back to ASUS Router app (Android)")
        try:
            self.web_driver.activate_app(ANDROID_APP_PACKAGE)
        except Exception as e:
            logger.warn("Failed to activate ASUS Router app: %s", e)
            return

        Utils.delay(delay)

    def _android_start_wifi_settings(self) -> bool:
        """Best-effort: open Wi-Fi settings screen."""
        if not (self.is_exist() and app.is_android()):
            return False

        # Prefer direct intent to Wi-Fi settings.
        try:
            self.web_driver.execute_script(
                "mobile: shell",
                {
                    "command": "am",
                    "args": ["start", "-a", "android.settings.WIFI_SETTINGS"],
                },
            )
            return True
        except Exception:
            pass

        # Fallback: try known Wi-Fi settings activity.
        try:
            self.web_driver.start_activity("com.android.settings", ".wifi.WifiSettings")
            return True
        except Exception:
            # Do not treat opening Settings home as success; caller will run UI navigation.
            return False

    def _android_click_entry_like(self, el) -> bool:
        """Click the row/container for a settings entry without toggling switches."""
        try:
            cls = el.get_attribute("className") or ""
            if "Switch" in cls or "CheckBox" in cls:
                return False
        except Exception:
            pass

        cur = el
        for _ in range(5):
            try:
                cls = cur.get_attribute("className") or ""
                clickable = cur.get_attribute("clickable")
                if clickable == "true" and (
                    "Switch" not in cls and "CheckBox" not in cls
                ):
                    cur.click()
                    return True
            except Exception:
                pass

            try:
                cur = cur.find_element(AppiumBy.XPATH, "..")
            except Exception:
                break

        try:
            el.click()
            return True
        except Exception:
            return False

    def _android_find_and_tap_text(
        self, text_candidates: list[str], *, timeout=2
    ) -> bool:
        import time as _time

        for t in text_candidates:
            xpath = f'//*[@text="{t}" or @content-desc="{t}"]'

            end_at = _time.time() + float(timeout)
            while _time.time() < end_at:
                try:
                    elements = self.web_driver.find_elements(AppiumBy.XPATH, xpath)
                except Exception:
                    elements = []

                for el in elements:
                    try:
                        if (
                            el
                            and el.is_displayed()
                            and self._android_click_entry_like(el)
                        ):
                            return True
                    except Exception:
                        continue

                Utils.delay(0.2)
        return False

    def _android_scroll_text_into_view(self, text: str) -> bool:
        if not (self.is_exist() and app.is_android()):
            return False

        try:
            ui = (
                "new UiScrollable(new UiSelector().scrollable(true))"
                f'.scrollTextIntoView("{text}")'
            )
            el = self.web_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
            if el and el.is_displayed():
                el.click()
                return True
        except Exception:
            return False

        return False

    def connect_android_wifi(self, ssid, password=None):
        if not (self.is_exist() and app.is_android()):
            return

        # step 1: open Android Settings
        self.goto_android_settings_app(delay=2)

        # step 2: open Wi-Fi settings screen
        if self._android_start_wifi_settings():
            Utils.delay(2)
        else:
            # UI fallback path varies by Android version/OEM.
            # Follow real device flows:
            # - Phone A: Network & internet > Internet
            # - Phone B: Connections > WiFi

            def _try_flow(*, first: list[str], second: list[str]) -> bool:
                if not self._android_find_and_tap_text(first, timeout=2):
                    return False
                Utils.delay(1)
                if not self._android_find_and_tap_text(second, timeout=2):
                    return False
                Utils.delay(2)
                return True

            opened = _try_flow(
                first=["Network & internet", "網路和網際網路"],
                second=["Internet", "網際網路"],
            )

            if not opened:
                # Reset to Settings home for the next attempt.
                self.goto_android_settings_app(delay=1)
                opened = _try_flow(
                    first=["Connections", "連線", "連接"],
                    second=[
                        "WiFi",
                        "Wi‑Fi",
                        "Wi-Fi",
                        "WLAN",
                        "無線網路",
                    ],
                )

            if not opened:
                logger.warn("Unable to navigate to Wi-Fi settings via UI fallback")

        # step 3: find SSID and tap it (scroll if needed)
        ssid_tapped = False

        # Try direct XPath lookup first.
        try:
            el = self.get_element_by_xpath(f'//*[@text="{ssid}"]', timeout=2)
            if el and el.is_displayed():
                el.click()
                ssid_tapped = True
        except Exception:
            pass

        if not ssid_tapped:
            # Try UiScrollable (more reliable for long lists)
            ssid_tapped = self._android_scroll_text_into_view(ssid)

        if not ssid_tapped:
            raise Exception(f"SSID '{ssid}' not found in Wi-Fi list")

        logger.info(f"Found and tapped SSID '{ssid}' in Wi-Fi settings")

        # Wait a bit for the network dialog/page to appear.
        Utils.delay(1)
        for _ in range(30):
            try:
                # Password field or a connect button indicates the dialog is ready.
                if self.web_driver.find_elements(
                    AppiumBy.XPATH,
                    "//android.widget.EditText | //*[@resource-id='android:id/button1']",
                ):
                    break
            except Exception:
                pass
            Utils.delay(0.2)

        # step 4: input password and connect if needed
        if password is not None and str(password) != "":
            pw_field = None

            # Prefer password-specific selectors first.
            ui_candidates = [
                'new UiSelector().className("android.widget.EditText").resourceIdMatches(".*password.*")',
                'new UiSelector().className("android.widget.EditText").descriptionContains("password")',
            ]
            for ui in ui_candidates:
                try:
                    el = self.web_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                    if el and el.is_displayed():
                        pw_field = el
                        break
                except Exception:
                    pass

            if pw_field is None:
                for xp in (
                    "//android.widget.EditText[contains(@resource-id,'password') or contains(@content-desc,'password') or contains(@hint,'password')]",
                    "//*[@resource-id='com.android.settings:id/password']",
                    "//*[@resource-id='com.samsung.android.settings:id/password']",
                    "//*[@resource-id='com.android.settings:id/edittext']",
                    "//*[@resource-id='com.samsung.android.settings:id/edittext']",
                    "//android.widget.EditText",
                ):
                    try:
                        el = self.get_element_by_xpath(xp, timeout=2)
                        if el and el.is_displayed():
                            pw_field = el
                            break
                    except Exception:
                        pass

            if pw_field:
                try:
                    pw_field.click()
                    pw_field.clear()
                except Exception:
                    pass
                pw_field.send_keys(str(password))
            else:
                logger.warn("Password field not found; attempting to connect anyway")

        # Tap connect/join/save if present
        if self._android_find_and_tap_text(
            ["Connect", "連線", "加入", "Join", "Save", "儲存"], timeout=2
        ):
            logger.info("Tapped Connect/Join/Save button in Wi-Fi dialog")
            Utils.delay(2)

        logger.info("Delaying after Wi-Fi connection attempt...")
        Utils.delay(10)

    def connect_ios_wifi(self, ssid, password=None):
        if not (self.is_exist() and app.is_ios()):
            return

        def _tap_center(el, *, name: str = "element") -> bool:
            """Best-effort tap for iOS/iPadOS: prefer coordinate tap to avoid non-hittable staticText."""
            if el is None:
                return False
            try:
                rect = getattr(el, "rect", None) or {}
                x = rect.get("x")
                y = rect.get("y")
                w = rect.get("width")
                h = rect.get("height")
                if None not in (x, y, w, h) and w and h:
                    cx = int(x + w / 2)
                    cy = int(y + h / 2)
                    self.web_driver.execute_script(
                        "mobile: tap", {"x": cx, "y": cy}
                    )
                    return True
            except Exception:
                pass

            try:
                el.click()
                return True
            except Exception as e:
                logger.warn(f"Failed to tap {name}: {e}")
                return False

        def _wifi_table_rect():
            """Return rect of Wi-Fi networks list area (important on iPad split layout)."""
            # iPadOS Settings often has multiple tables (left sidebar + right content).
            # Pick the largest visible table as the most likely Wi-Fi list container.
            try:
                tables = self.web_driver.find_elements(
                    AppiumBy.XPATH, "//XCUIElementTypeTable"
                )
            except Exception:
                tables = []

            best_rect = None
            best_area = 0
            for t in tables:
                try:
                    if not t or not t.is_displayed():
                        continue
                    rect = getattr(t, "rect", None) or {}
                    w = rect.get("width") or 0
                    h = rect.get("height") or 0
                    area = float(w) * float(h)
                    if area > best_area and w > 0 and h > 0:
                        best_area = area
                        best_rect = rect
                except Exception:
                    continue

            if best_rect:
                return best_rect

            for xp in ("//XCUIElementTypeScrollView",):
                try:
                    el = self.get_element_by_xpath(xp, timeout=1)
                    if el and el.is_displayed():
                        rect = getattr(el, "rect", None)
                        if rect and rect.get("width") and rect.get("height"):
                            return rect
                except Exception:
                    pass
            return None

        def _wait_wifi_join_ui(timeout_s: float = 3.0) -> bool:
            import time as _time

            end_at = _time.time() + float(timeout_s)
            while _time.time() < end_at:
                try:
                    if self.web_driver.find_elements(
                        AppiumBy.XPATH,
                        "//XCUIElementTypeSecureTextField | //XCUIElementTypeButton[@name='Join'] | //XCUIElementTypeStaticText[@name='Password']",
                    ):
                        return True
                except Exception:
                    pass
                Utils.delay(0.2)
            return False

        # step 1: goto ios settings app
        self.goto_ios_settings_app()

        # step 2: enter wifi settings page
        # iPadOS Settings often has a split layout; avoid ultra-short swipes.
        self.swipe_down(progress={"begin": 0.2, "end": 1.0}, duration=0.2)

        wifi_xpath_candidates = [
            # Prefer tapping the Cell (works on iPhone/iPad and avoids tapping label only)
            '//XCUIElementTypeCell[@name="Wi-Fi" or .//XCUIElementTypeStaticText[@name="Wi-Fi"]]',
            '//XCUIElementTypeButton[@name="Wi-Fi"]',
            '//XCUIElementTypeStaticText[@name="Wi-Fi"]',
            '//XCUIElementTypeButton[@name="com.apple.settings.wifi"]',
        ]

        wifi_element = None
        for xpath in wifi_xpath_candidates:
            try:
                element = self.get_element_by_xpath(xpath)
                if element and element.is_displayed():
                    wifi_element = element
                    break
            except Exception:
                pass

        if wifi_element:
            _tap_center(wifi_element, name="Wi-Fi entry")
            logger.info("Found and tapped Wi-Fi entry in Settings")
            Utils.delay(5)
        else:
            logger.warn("Cannot find Wi-Fi entry in Settings.")

        # step 3: find and tap target SSID, scroll if not visible
        table_rect = _wifi_table_rect()
        self.swipe_down(
            rect=table_rect, progress={"begin": 0.2, "end": 1.0}, duration=0.2
        )

        max_scroll_attempts = 10
        ssid_element = None
        for i in range(max_scroll_attempts):
            # Prefer the whole Cell row instead of StaticText (StaticText is often not tappable on iPad)
            try:
                element = self.get_element_by_ios_class_chain(
                    f'**/XCUIElementTypeCell[`name == "{ssid}"`]' 
                )
                if element and element.is_displayed():
                    logger.debug(f"Found SSID '{ssid}' cell using class chain")
                    ssid_element = element
                    break
            except Exception:
                pass

            try:
                element = self.get_element_by_xpath(
                    f'//XCUIElementTypeCell[@name="{ssid}" or .//XCUIElementTypeStaticText[@name="{ssid}"]]'
                )
                if element and element.is_displayed():
                    logger.debug(f"Found SSID '{ssid}' cell using XPath")
                    ssid_element = element
                    break
            except Exception:
                pass

            logger.debug(
                f"SSID '{ssid}' not found, swiping up to scroll the list (attempt {i + 1}/{max_scroll_attempts})"
            )
            self.swipe_up(rect=table_rect, progress={"begin": 0.1, "end": 0.9}, duration=1.0)
            Utils.delay(1)

        if ssid_element and ssid_element.is_displayed():
            # Some devices show the label but the tap doesn't register; use coordinate tap + verify.
            _tap_center(ssid_element, name=f"SSID '{ssid}'")
            if not _wait_wifi_join_ui(timeout_s=2.0):
                logger.warn(
                    f"Tapped SSID '{ssid}' but no join/password UI detected; retrying tap"
                )
                Utils.delay(0.5)
                _tap_center(ssid_element, name=f"SSID '{ssid}' (retry)")
            logger.info(f"Found and tapped SSID '{ssid}'")
        else:
            raise Exception(f"SSID '{ssid}' not found in Wi-Fi list after scrolling")

        # step 4: input password if needed
        if password:
            Utils.delay(1)

            join_button = None
            try:
                join_button = self.get_element_by_xpath(
                    '//XCUIElementTypeButton[@name="Join"]', timeout=2
                )
            except Exception:
                join_button = None

            try:
                password_field = self.get_element_by_xpath(
                    "//XCUIElementTypeSecureTextField", timeout=2
                )
                if password_field:
                    _tap_center(password_field, name="Wi-Fi password field")
                    try:
                        password_field.clear()
                    except Exception:
                        pass
                    password_field.send_keys(password)
                else:
                    raise Exception("Wi-Fi password field not found")

                if join_button:
                    _tap_center(join_button, name="Join")
                else:
                    logger.warn("Join button not found; password entered but cannot tap Join")
            except Exception as e:
                raise Exception(f"Wi-Fi password input failed: {e}")

        logger.info(f"Delaying after Wi-Fi connection attempt...")
        Utils.delay(10)

    def connect_wifi(self, ssid, password=None):
        if app.is_ios():
            try:
                self.connect_ios_wifi(ssid, password)
            finally:
                self.goto_ios_asusrouter_app()
        elif app.is_android():
            try:
                self.connect_android_wifi(ssid, password)
            finally:
                self.goto_android_asusrouter_app()


# Singleton
driver = Driver()
