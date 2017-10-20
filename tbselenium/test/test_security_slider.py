import unittest
import pytest

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from tbselenium.test.fixtures import TBDriverFixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH

SEC_SLIDER_PREF = "extensions.torbutton.security_slider"


class TBSecuritySlider(unittest.TestCase):

    def test_security_slider_settings_hi(self):
        """Slider setting `High` should disable JavaScript."""
        with TBDriverFixture(TBB_PATH,
                             pref_dict={SEC_SLIDER_PREF: 1}) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security slider should disable JavaScript")
            except (NoSuchElementException, TimeoutException):
                pass

    def test_security_slider_settings_low_mid(self):
        # TODO: test other features to distinguish between levels
        # 2: medium-high, 3: medium-low, 4: low (default)
        for sec_slider_setting in [2, 3, 4]:
            slider_dict = {SEC_SLIDER_PREF: sec_slider_setting}
            with TBDriverFixture(TBB_PATH, pref_dict=slider_dict) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)


if __name__ == "__main__":
    unittest.main()
