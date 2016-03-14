import unittest
from time import sleep
from os import environ
from os.path import getsize

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbbselenium import common as cm
from tbbselenium.tbdriver import TorBrowserDriver
from tbbselenium.utils import get_hash_of_directory

WAIT_TIME = 60

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere.js
HTTP_URL = "http://httpbin.org/"
HTTPS_URL = "https://httpbin.org/"

WEBGL_URL = "https://developer.mozilla.org/samples/webgl/sample1/index.html"

TEST_URL = "http://check.torproject.org"

TBB_PATH = environ.get('TBB_PATH')
if TBB_PATH is None:
    raise RuntimeError("Environment variable `TBB_PATH` with TBB directory not found.")


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TorBrowserDriver(TBB_PATH, capture_screen=True)

    def tearDown(self):
        self.tb_driver.quit()

    def test_tbdriver_simple_visit(self):
        """Visiting checktor.torproject.org with TB driver should detect Tor IP."""
        self.tb_driver.get(TEST_URL)
        self.tb_driver.implicitly_wait(WAIT_TIME)
        h1_on = self.tb_driver.find_element_by_css_selector("h1.on")
        self.assertTrue(h1_on)

    def test_tbdriver_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_hash_before = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        tb_driver = TorBrowserDriver(TBB_PATH)
        tb_driver.get(TEST_URL)
        tb_driver.quit()
        profile_hash_after = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        self.assertEqual(profile_hash_before, profile_hash_after)

    def test_httpseverywhere(self):
        """Visiting an HTTP page with HTTPSEverywhere should force HTTPS version."""
        self.tb_driver.get(HTTP_URL)
        sleep(1)
        try:
            WebDriverWait(self.tb_driver, WAIT_TIME).until(EC.title_contains("httpbin"))
        except TimeoutException:
            self.fail("The title should contain httpbin")
        self.assertEqual(self.tb_driver.current_url, HTTPS_URL)

    def test_noscript(self):
        """Visiting a WebGL page with NoScript should disable WebGL."""
        webgl_test_url = WEBGL_URL
        self.tb_driver.get(webgl_test_url)
        try:
            WebDriverWait(self.tb_driver, WAIT_TIME).until(EC.alert_is_present())
        except TimeoutException:
            self.fail("WebGL error alert should be present")
        self.tb_driver.switch_to.alert.dismiss()
        self.tb_driver.implicitly_wait(WAIT_TIME / 2)
        el = self.tb_driver.find_element_by_class_name("__noscriptPlaceholder__ ")
        self.assertTrue(el)
        # sanity check for the above test
        self.assertRaises(NoSuchElementException,
                          self.tb_driver.find_element_by_class_name, "__nosuch_class_exist")

    def test_https_everywhere_disabled(self):
        """Test to make sure the HTTP->HTTPS redirection observed in the
        previous test (test_tb_extensions) is really due to HTTPSEverywhere -
        but not because the site is HTTPS by default. See, the following:
        https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere-disabled.js
        """
        ff_driver = webdriver.Firefox()
        ff_driver.get(HTTP_URL)
        sleep(1)
        # make sure it doesn't redirect to https
        self.assertEqual(ff_driver.current_url, HTTP_URL)
        ff_driver.quit()

    def test_screen_capture(self):
        """Check for screenshot after visit."""
        screenshot_path = "screenshot.png"
        self.tb_driver.get(TEST_URL)
        # A blank page for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture on the other hand, is ~57KB. If the capture
        # is not blank it should be at least greater than 30KB.
        self.assertGreater(getsize(screenshot_path), 30000)


if __name__ == "__main__":
    unittest.main()
