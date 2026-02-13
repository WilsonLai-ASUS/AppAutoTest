# test_first_login.py

"""
測試首次登錄流程
"""

import sys
from tests.test_base import TestBase
from common import (
    dut,
    Element,
    ElementFinder,
    logger,
    Result,
    ResultCode,
    screenshot,
    Utils,
)


class TestFirstLogin(TestBase):

    def test(self) -> Result:

        def steps():
            Utils.delay(4)

            # find login button
            login_button = ElementFinder.FirstLoginPage.get_login_button()

            self.check(
                login_button.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                "Login button not found",
            )

            self.check(
                login_button.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                "Login button not tappable",
            )

            # find username text field
            username_text_field = ElementFinder.LoginPage.get_username_text_field()

            self.check(
                username_text_field.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                "Username text field not found",
            )

            self.check(
                username_text_field.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                "Username text field not tappable",
            )

            self.check(
                username_text_field.send_keys(dut.username),
                ResultCode.ELEMENT_NOT_TYPABLE,
                "Username text field not typable",
            )

            # find password text field
            password_text_field = ElementFinder.LoginPage.get_password_text_field()

            self.check(
                password_text_field.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                "Password text field not found",
            )
            self.check(
                password_text_field.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                "Password text field not tappable",
            )
            self.check(
                password_text_field.send_keys(dut.password),
                ResultCode.ELEMENT_NOT_TYPABLE,
                "Password text field not typable",
            )

            # find login button
            login_button = ElementFinder.LoginPage.get_login_button()

            self.check(
                login_button.is_exist(),
                ResultCode.ELEMENT_NOT_FOUND,
                "Login button not found",
            )

            self.check(
                login_button.tap(),
                ResultCode.ELEMENT_NOT_TAPPABLE,
                "Login button not tappable",
            )

            Utils.delay(4)

        return self.run_test(steps)


if __name__ == "__main__":
    test = TestFirstLogin(sys.argv)
    test.finish(test.test())
