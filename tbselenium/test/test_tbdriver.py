import tempfile
import unittest
from os import remove
from os.path import getsize, exists
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH
from tbselenium.utils import get_hash_of_directory, start_xvfb, stop_xvfb

TEST_LONG_WAIT = 60

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere.js
HTTP_URL = "http://httpbin.org/"
HTTPS_URL = "https://httpbin.org/"

WEBGL_URL = "https://developer.mozilla.org/samples/webgl/sample1/index.html"


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TorBrowserDriver(TBB_PATH, virt_display=cm.DEFAULT_XVFB_WINDOW_SIZE)

    def tearDown(self):
        self.tb_driver.quit()

    def test_tbdriver_simple_visit(self):
        """checktor.torproject.org should detect Tor IP."""
        self.tb_driver.get(cm.CHECK_TPO_URL)
        self.tb_driver.implicitly_wait(TEST_LONG_WAIT)
        h1_on = self.tb_driver.find_element_by_css_selector("h1.on")
        self.assertTrue(h1_on)

    def test_tbdriver_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_hash_before = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        self.tb_driver.get(cm.CHECK_TPO_URL)
        profile_hash_after = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        self.assertEqual(profile_hash_before, profile_hash_after)

    def test_httpseverywhere(self):
        """Visiting an HTTP page with HTTPSEverywhere should force HTTPS version."""
        self.tb_driver.get(HTTP_URL)
        sleep(1)
        try:
            WebDriverWait(self.tb_driver, TEST_LONG_WAIT).until(EC.title_contains("httpbin"))
        except TimeoutException:
            self.fail("The title should contain httpbin")
        self.assertEqual(self.tb_driver.current_url, HTTPS_URL)

    def test_noscript(self):
        """Visiting a WebGL page with NoScript should disable WebGL."""
        self.tb_driver.get(WEBGL_URL)
        try:
            WebDriverWait(self.tb_driver, TEST_LONG_WAIT).until(EC.alert_is_present())
        except TimeoutException:
            self.fail("WebGL error alert should be present")
        self.tb_driver.switch_to.alert.dismiss()
        self.tb_driver.implicitly_wait(TEST_LONG_WAIT / 2)
        el = self.tb_driver.find_element_by_class_name("__noscriptPlaceholder__ ")
        self.assertTrue(el)
        # sanity check for the above test
        self.assertRaises(NoSuchElementException,
                          self.tb_driver.find_element_by_class_name, "__nosuch_class_exist")


class ScreenshotTest(unittest.TestCase):
    def setUp(self):
        _, self.temp_file = tempfile.mkstemp()

    def tearDown(self):
        if exists(self.temp_file):
            remove(self.temp_file)

    def test_screen_capture(self):
        """Check for screenshot after visit."""
        TorBrowserDriver.add_exception(cm.CHECK_TPO_URL)
        self.tb_driver = TorBrowserDriver(TBB_PATH, virt_display=cm.DEFAULT_XVFB_WINDOW_SIZE)
        self.tb_driver.get(cm.CHECK_TPO_URL)
        sleep(3)
        try:
            self.tb_driver.get_screenshot_as_file(self.temp_file)
        except Exception as e:
            self.fail("An exception occurred while taking screenshot: %s" % e)
        self.tb_driver.quit()
        # A blank page for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture on the other hand, is ~57KB. If the capture
        # is not blank it should be at least greater than 20KB.
        self.assertGreater(getsize(self.temp_file), 20000)


class HTTPSEverywhereTest(unittest.TestCase):
    def test_https_everywhere_disabled(self):
        """Test to make sure the HTTP->HTTPS redirection observed in the
        previous test (test_tb_extensions) is really due to HTTPSEverywhere -
        but not because the site is HTTPS by default. See, the following:
        https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere-disabled.js
        """
        display = start_xvfb(1280, 800)
        ff_driver = webdriver.Firefox()
        ff_driver.get(HTTP_URL)
        sleep(1)
        # make sure it doesn't redirect to https
        self.assertEqual(ff_driver.current_url, HTTP_URL)
        ff_driver.quit()
        stop_xvfb(display)


if __name__ == "__main__":
    unittest.main()
