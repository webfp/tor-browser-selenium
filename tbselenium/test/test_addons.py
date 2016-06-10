import os
import unittest
import pytest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture


class HTTPSEverywhereTest(unittest.TestCase):

    # Test URLs are taken from the TBB test suite
    # https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/marionette/tor_browser_tests/test_https-everywhere.py#n18
    HE_HTTP_URL = "http://www.freedomboxfoundation.org/thanks/"
    HE_HTTPS_URL = "https://www.freedomboxfoundation.org/thanks/"
    TEST_LONG_WAIT = 60

    def test_https_everywhere_redirection(self):
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure(self.HE_HTTP_URL)
            WebDriverWait(driver, self.TEST_LONG_WAIT).\
                until(EC.title_contains("thanks"))
            self.assertEqual(driver.current_url, self.HE_HTTPS_URL)

    def test_https_everywhere_disabled(self):
        """Make sure the HTTP->HTTPS redirection in the above test
        is due to HTTPSEverywhere - not because the site is forwarding
        to HTTPS by default.

        We have to find another test site if this test starts to fail.
        """

        disable_HE_pref = {"extensions.https_everywhere.globalEnabled": False}
        with TBDriverFixture(TBB_PATH, pref_dict=disable_HE_pref) as driver:
            driver.load_url_ensure(self.HE_HTTP_URL, 1)
            self.assertEqual(driver.current_url, self.HE_HTTP_URL)


class NoScriptTest(unittest.TestCase):

    WEBGL_CHECK_JS = "var cvs = document.createElement('canvas');\
                    return cvs.getContext('experimental-webgl');"

    @pytest.mark.skipif(cm.TRAVIS, reason="CI doesn't support WebGL")
    def test_noscript(self):
        """NoScript should disable WebGL."""
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL,
                                   wait_for_page_body=True)
            webgl_support = driver.execute_script(self.WEBGL_CHECK_JS)
            self.assertIsNone(webgl_support)

    @pytest.mark.skipif(cm.TRAVIS, reason="CI doesn't support WebGL")
    def test_noscript_webgl_enabled(self):
        """Make sure that when we disable NoScript's WebGL blocking,
        WebGL becomes available. This is to the test method we
        use in test_noscript is sane.
        """
        disable_NS_webgl_pref = {"noscript.forbidWebGL": False}
        with TBDriverFixture(TBB_PATH,
                             pref_dict=disable_NS_webgl_pref) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, wait_for_page_body=True)
            webgl_support = driver.execute_script(self.WEBGL_CHECK_JS)
            self.assertIn("getSupportedExtensions", webgl_support)


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
