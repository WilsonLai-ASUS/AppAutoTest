# screenshot.py

"""
Screenshot utility for taking screenshots during tests.
"""

from datetime import datetime


class Screenshot:
    dir = None

    def __init__(self):
        pass

    def set_dir(self, dir):
        self.dir = dir

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%H%M%S")

    def take(self, prefix="screenshot"):
        from .driver import driver

        if driver.is_exist:
            filepath = f"{self.dir}/{prefix}_{self.timestamp()}.png"
            driver.save_screenshot(filepath=filepath)
            print(f"Screenshot saved: {filepath}")
        else:
            print("Driver not initialized, cannot take screenshot.")


# Singleton
screenshot = Screenshot()
