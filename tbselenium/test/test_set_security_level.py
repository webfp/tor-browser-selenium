import unittest
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL, CI_ALPHA_TEST
from tbselenium.utils import set_security_level
from tbselenium.utils import SECURITY_HIGH, SECURITY_MEDIUM, SECURITY_LOW


class SecurityLevelTest(unittest.TestCase):

    def test_set_security_low(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is disabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Standard")
            except (NoSuchElementException, TimeoutException):
                pass

    # TODO: find a better way to test for this
    def test_set_security_medium(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is disabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Safer")
            except (NoSuchElementException, TimeoutException):
                pass

    @pytest.mark.skipif(
        CI_ALPHA_TEST,
        reason="Not compatible with the current alpha (10.5a1)")
    def test_set_security_high(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Safest")
            except (NoSuchElementException, TimeoutException):
                pass


if __name__ == "__main__":
    unittest.main()
