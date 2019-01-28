import unittest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL
from tbselenium.utils import disable_js


class JSDisableTest(unittest.TestCase):

    def test_disable_js(self):
        with TBDriverFixture(TBB_PATH) as driver:
            disable_js(driver)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("JavaScript is not disabled")
            except (NoSuchElementException, TimeoutException):
                pass


if __name__ == "__main__":
    unittest.main()
