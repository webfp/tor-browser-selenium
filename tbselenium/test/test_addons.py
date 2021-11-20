import os
import unittest
import pytest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture


class HTTPSEverywhereTest(unittest.TestCase):

    # Test idea is taken from the TBB test suite
    # https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/marionette/tor_browser_tests/test_https-everywhere.py#n18
    HE_HTTP_URL = "http://httpbin.org/"
    HE_HTTPS_URL = "https://httpbin.org/"
    TEST_LONG_WAIT = 60

    def test_https_everywhere_redirection(self):
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure(self.HE_HTTP_URL)
            WebDriverWait(driver, self.TEST_LONG_WAIT).\
                until(EC.title_contains("httpbin"))
            self.assertEqual(driver.current_url, self.HE_HTTPS_URL)


class CustomExtensionTest(unittest.TestCase):

    def test_should_install_custom_extension(self):
        XPI_NAME = "borderify.xpi"  # sample extension based on:
        # https://github.com/mdn/webextensions-examples/tree/master/borderify
        # Currently we only install the addon.
        # TODO: Improve by checking the expected outcome
        # (e.g. different borders due to borderify addon).
        test_dir = os.path.dirname(os.path.realpath(__file__))
        xpi_path = os.path.join(test_dir, "test_data", XPI_NAME)
        with TBDriverFixture(TBB_PATH,
                             extensions=[xpi_path]) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)


if __name__ == "__main__":
    unittest.main()
