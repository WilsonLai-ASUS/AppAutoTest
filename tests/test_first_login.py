# test_first_login.py

"""
測試首次登錄流程
"""

import sys
from tests.test_base import TestBase
from common import Result
import tests.pages.sky_tree_page as sky_tree_page
import tests.pages.login_page as login_page

class TestFirstLogin(TestBase):

    def test(self) -> Result:

        def steps():
            sky_tree_page.tap_login_button(self)
            login_page.login(self)
            
        return self.run_test(steps)


def main(argv=None):
    test = TestFirstLogin(argv or sys.argv)
    test.finish(test.test())


if __name__ == "__main__":
    main()
