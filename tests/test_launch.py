# test_launch.py

"""
測試 App 啟動
"""

import sys
from tests.test_base import TestBase
from common import Result


class TestLaunch(TestBase):

    def test(self) -> Result:

        def steps():
            pass

        return self.run_test(steps)


def main(argv=None):
    test = TestLaunch(argv or sys.argv)
    test.finish(test.test())


if __name__ == "__main__":
    main()
