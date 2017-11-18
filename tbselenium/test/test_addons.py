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


class NoScriptTest(unittest.TestCase):

    @pytest.mark.skipif(cm.TRAVIS, reason="CI doesn't support WebGL")
    def test_noscript_should_disable_webgl(self):
        webgl_status_disabled = ("This browser supports WebGL 1, "
                                 "but it is disabled or unavailable.")
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure("http://webglreport.com/",
                                   wait_for_page_body=True)
            status = driver.find_element_by(".header > p").text
            self.assertIn(webgl_status_disabled, status)

    @pytest.mark.skipif(cm.TRAVIS, reason="CI doesn't support WebGL")
    def test_noscript_disable_webgl_block(self):
        """WebGL should work when we disable NoScript's WebGL blocking."""
        disable_NS_webgl_pref = {"noscript.forbidWebGL": False}
        webgl_status_enabled = ("This browser supports WebGL 1")
        with TBDriverFixture(TBB_PATH,
                             pref_dict=disable_NS_webgl_pref) as driver:
            driver.load_url_ensure("http://webglreport.com/",
                                   wait_for_page_body=True)
            status = driver.find_element_by(".header > p").text
            self.assertIn(webgl_status_enabled, status)


class CustomExtensionTest(unittest.TestCase):

    def test_should_install_custom_extension(self):
        # We test if we can install the extension.
        # We should improve the test by checking the expected outcome.
        test_dir = os.path.dirname(os.path.realpath(__file__))
        xpi_name = "xulschoolhello1.xpi"  # sample extension taken from:
        # https://developer.mozilla.org/en-US/Add-ons/Overlay_Extensions/XUL_School/Getting_Started_with_Firefox_Extensions#Extension_Contents  # noqa
        xpi_path = os.path.join(test_dir, "test_data", xpi_name)
        with TBDriverFixture(TBB_PATH,
                             extensions=[xpi_path]) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)


if __name__ == "__main__":
    unittest.main()
