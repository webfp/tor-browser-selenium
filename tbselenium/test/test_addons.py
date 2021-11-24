import unittest
import pytest
from os.path import dirname, realpath, join
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture


class TBAddonsTest(unittest.TestCase):

    # Test idea is taken from the TBB test suite
    # https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/marionette/tor_browser_tests/test_https-everywhere.py#n18
    HE_HTTP_URL = "http://httpbin.org/"
    HE_HTTPS_URL = "https://httpbin.org/"
    TEST_LONG_WAIT = 60

    def get_list_of_installed_addons(self, driver):
        found_addons = []
        driver.load_url_ensure("about:addons")
        addons = driver.find_elements(By.CLASS_NAME, "addon-name")
        for addon in addons:
            found_addons.append(addon.text)
        return found_addons

    def test_https_everywhere_redirection(self):
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure(self.HE_HTTP_URL)
            WebDriverWait(driver, self.TEST_LONG_WAIT).\
                until(EC.title_contains("httpbin"))
            self.assertEqual(driver.current_url, self.HE_HTTPS_URL)

    def test_builtin_addons_should_come_installed(self):
        """Make sure that the built-in addons come installed."""
        EXPECTED_ADDONS = set(['HTTPS Everywhere', 'NoScript'])
        found_addons = []
        with TBDriverFixture(TBB_PATH) as driver:
            found_addons = self.get_list_of_installed_addons(driver)
            assert EXPECTED_ADDONS == set(found_addons)

    def test_should_install_custom_extension(self):
        XPI_NAME = "borderify.xpi"  # sample extension based on:
        # https://github.com/mdn/webextensions-examples/tree/master/borderify
        test_dir = dirname(realpath(__file__))
        xpi_path = join(test_dir, "test_data", XPI_NAME)

        with TBDriverFixture(TBB_PATH, extensions=[xpi_path]) as driver:
            assert 'Borderify' in self.get_list_of_installed_addons(driver)


if __name__ == "__main__":
    unittest.main()
