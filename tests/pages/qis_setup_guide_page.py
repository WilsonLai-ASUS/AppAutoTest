"""qis setup guide page"""

from tests.test_base import TestBase
from common import Element, logger, ResultCode, Utils, app


def get_next_button() -> Element:
    return Element(ios_button_name="Next")


def tap_next_button(test: TestBase):
    # find next button
    next_button = get_next_button()

    test.check(
        next_button.is_exist(),
        ResultCode.ELEMENT_NOT_FOUND,
        "Next button not found",
    )

    test.check(
        next_button.tap(),
        ResultCode.ELEMENT_NOT_TAPPABLE,
        "Next button not tappable",
    )

    logger.info("Tapped 'Next' button")
