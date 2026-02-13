# test_login.py
"""
ASUS Router App 登入測試
"""

from cmath import rect
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ========== 配置區 ==========
APPIUM_SERVER = 'http://127.0.0.1:4723'
DEVICE_UDID = '00008120-000125DE145BC01E'
BUNDLE_ID = 'com.asus.asusrouter'

# 測試帳號
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'asus#12345'

# 元素定位器（根據您的 App 修改）
OPEN_LOGIN_BUTTON = "登入按鈕名稱"  # 替換為實際名稱
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"
LOGIN_BUTTON = "登入"
SUCCESS_INDICATOR = "首頁"

def setup_driver():
    """初始化 Appium Driver"""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone"
    options.automation_name = "XCUITest"
    options.udid = DEVICE_UDID
    options.bundle_id = BUNDLE_ID
    options.new_command_timeout = 3600
    
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    return driver

def get_elements_by_xpath(driver, xpath, timeout=1):
    wait = WebDriverWait(driver, timeout)
    try:
        elements = wait.until(EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath)))
        return elements  # list，可能有多個元素
    except:
        return []  # 找不到元素就回傳空 list

def get_home_navigation_bar_add_button(driver):
    buttons = get_elements_by_xpath(driver, "//XCUIElementTypeNavigationBar//XCUIElementTypeButton[@name='Add']")
    return buttons[-1] if buttons else None
    
def tap_element_center(driver, element, delay=1):
    rect = element.rect
    x = rect["x"] + rect["width"] // 2
    y = rect["y"] + rect["height"] // 2
    driver.execute_script("mobile: tap", {"x": x, "y": y})

def save_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"📸 已保存截圖: {filename}")
    
def test_login():
    """測試登入流程"""
    driver = setup_driver()
    
    try:
        print("→ 開始測試登入流程...")
        wait = WebDriverWait(driver, 10)
        
        # 等待 App 啟動
        time.sleep(3)
        print("✓ App 已啟動")
        
        # 步驟 1: 點擊開啟登入視窗
        time.sleep(4)

        print("→ 尋找 Add 按鈕")
        add_button = get_home_navigation_bar_add_button(driver)

        if not add_button:
            raise RuntimeError("找不到 Add 按鈕")
        
        print("✓ 找到 Add 按鈕，準備點擊")
        tap_element_center(driver, add_button)
        
        print("→ 點擊 Add 按鈕完畢")
        time.sleep(2)
        print("✓ 登入視窗已開啟")
        
        # 步驟 2: 輸入用戶名
        print(f"→ 輸入用戶名: {TEST_USERNAME}")
        username_field = wait.until(
            EC.presence_of_element_located((AppiumBy.NAME, USERNAME_FIELD))
        )
        username_field.send_keys(TEST_USERNAME)
        print("✓ 用戶名已輸入")
        
        # 步驟 3: 輸入密碼
        print("→ 輸入密碼")
        password_field = driver.find_element(AppiumBy.NAME, PASSWORD_FIELD)
        password_field.send_keys(TEST_PASSWORD)
        print("✓ 密碼已輸入")
        
        # 步驟 4: 點擊登入按鈕
        print("→ 點擊登入按鈕")
        login_button = driver.find_element(AppiumBy.NAME, LOGIN_BUTTON)
        login_button.click()
        time.sleep(3)
        print("✓ 已點擊登入按鈕")
        
        # 步驟 5: 驗證登入成功
        print("→ 驗證登入結果...")
        try:
            success_element = wait.until(
                EC.presence_of_element_located((AppiumBy.NAME, SUCCESS_INDICATOR))
            )
            print("✅ 測試成功：登入完成！")
            return True
        except:
            print("❌ 測試失敗：未找到登入成功指示元素")
            driver.save_screenshot("login_failed.png")
            print("📸 已保存截圖: login_failed.png")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("📸 已保存截圖: error_screenshot.png")
        return False
        
    finally:
        print("→ 關閉測試 session...")
        driver.quit()
        print("✓ 測試結束")


if __name__ == "__main__":
    # 執行測試
    result = test_login()
    
    if result:
        print("\n" + "="*50)
        print("測試結果: ✅ 通過")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("測試結果: ❌ 失敗")
        print("="*50)
