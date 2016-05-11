import unittest
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By


class JSDisableTest(unittest.TestCase):

    def test_disable_js(self):
        # Disable javascript using the noscript pref
        # if we don't set torbutton.security_custom to True, torbutton
        # security slider will overwrite our modification and enable JS
        pref_dict = {"noscript.global": False,
                     "extensions.torbutton.security_custom": True}
        with TBDriverFixture(TBB_PATH, pref_dict=pref_dict) as driver:
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("JavaScript is not disabled")
            except (NoSuchElementException, TimeoutException):
                pass


if __name__ == "__main__":
    unittest.main()
