import tempfile
import unittest
from os import remove
from os.path import getsize, exists

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH
from tbselenium.utils import get_hash_of_directory, read_file, is_png
from tld.exceptions import TldBadUrl

TEST_LONG_WAIT = 60

WEBGL_URL = "https://developer.mozilla.org/samples/webgl/sample1/index.html"

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/marionette/tor_browser_tests/test_https-everywhere.py#n18
TEST_HTTP_URL = "http://www.freedomboxfoundation.org/thanks/"
TEST_HTTPS_URL = "https://www.freedomboxfoundation.org/thanks/"

MISSING_DIR = "_no_such_directory_"
MISSING_FILE = "_no_such_file_"


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TorBrowserDriver(TBB_PATH)

    def tearDown(self):
        self.tb_driver.quit()

    def test_tbdriver_simple_visit(self):
        """checktor.torproject.org should detect Tor IP."""
        self.tb_driver.load_url(cm.CHECK_TPO_URL)
        try:
            self.tb_driver.find_el_by_css("h1.on", 30)
        except TimeoutException as texc:
            self.fail("Can't find the network status on the page: %s" % texc)

    def test_tbdriver_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_hash_before = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        self.tb_driver.get(cm.CHECK_TPO_URL)
        profile_hash_after = get_hash_of_directory(cm.DEFAULT_TBB_PROFILE_PATH)
        self.assertEqual(profile_hash_before, profile_hash_after)

    def test_httpseverywhere(self):
        """HTTPSEverywhere should redirect to HTTPS version."""
        self.tb_driver.get(TEST_HTTP_URL)
        try:
            WebDriverWait(self.tb_driver, TEST_LONG_WAIT).\
                until(EC.title_contains("thanks"))
        except TimeoutException:
            self.fail("Unexpected page title %s" % self.tb_driver.title)
        self.assertEqual(self.tb_driver.current_url, TEST_HTTPS_URL)

    def test_noscript(self):
        """NoScript should disable WebGL."""
        self.tb_driver.get(WEBGL_URL)
        try:
            WebDriverWait(self.tb_driver, TEST_LONG_WAIT).\
                until(EC.alert_is_present())
        except TimeoutException:
            self.fail("WebGL error alert should be present")
        self.tb_driver.switch_to.alert.dismiss()
        try:
            self.tb_driver.find_el_by_css(".__noscriptPlaceholder__", 30)
        except TimeoutException as texc:
            self.fail("Can't find the __noscriptPlaceholder__: %s" % texc)


class TBDriverFailTest(unittest.TestCase):

    def test_should_raise_for_missing_paths(self):
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TorBrowserDriver()
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided None")

    def test_should_raise_for_missing_tbb_path(self):
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TorBrowserDriver(tbb_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "TBB path is not a directory %s" % MISSING_DIR)

    def test_should_raise_for_missing_fx_binary(self):
        temp_dir = tempfile.mkdtemp()
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=MISSING_FILE,
                             tbb_profile_path=temp_dir)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox binary %s" % MISSING_FILE)

    def test_should_raise_for_missing_fx_profile(self):
        _, temp_file = tempfile.mkstemp()
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=temp_file,
                             tbb_profile_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox profile dir %s" % MISSING_DIR)

    def test_should_raise_for_invalid_pref_dict(self):
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict="foo")
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=[1, 2])
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=(1, 2))

    def test_should_fail_with_wrong_socks_port(self):
        with TorBrowserDriver(TBB_PATH, socks_port=9999) as driver:
            driver.load_url(cm.CHECK_TPO_URL)
            self.assertEqual(driver.title, "Problem loading page")

    def test_should_raise_for_invalid_virtual_display_size(self):
        with self.assertRaises(ValueError):
            TorBrowserDriver(TBB_PATH, virt_display="foo")
        with self.assertRaises(ValueError):
            TorBrowserDriver(TBB_PATH, virt_display="800y600")
        with self.assertRaises(ValueError):
            TorBrowserDriver(TBB_PATH, virt_display="800-600")

    def test_should_raise_for_invalid_canvas_exceptions(self):
        with self.assertRaises(TldBadUrl):
            TorBrowserDriver(TBB_PATH, canvas_exceptions=["foo", "bar"])
        with self.assertRaises(TldBadUrl):
            TorBrowserDriver(TBB_PATH, canvas_exceptions=["foo.bar"])
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, canvas_exceptions=[1, 2])


class ScreenshotTest(unittest.TestCase):
    def setUp(self):
        _, self.temp_file = tempfile.mkstemp()

    def tearDown(self):
        if exists(self.temp_file):
            remove(self.temp_file)

    def test_screen_capture(self):
        """Make sure we can capture the screen."""
        with TorBrowserDriver(TBB_PATH,
                              canvas_exceptions=[cm.CHECK_TPO_URL]) as driver:
            # passing canvas_exceptions is not needed for TBB >= 4.5a3
            driver.load_url(cm.CHECK_TPO_URL, 3)
            driver.get_screenshot_as_file(self.temp_file)
        # A blank image for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture of the same page is ~57KB. If the capture
        # is not blank it should be at least greater than 20KB.
        self.assertGreater(getsize(self.temp_file), 20000)
        self.assertTrue(is_png(self.temp_file), "Doesn't look like a PNG file")


class TBDriverOptionalArgs(unittest.TestCase):

    def test_security_slider_settings_hi(self):
        security_high = {"extensions.torbutton.security_slider": 1}
        with TorBrowserDriver(TBB_PATH, pref_dict=security_high) as driver:
            driver.load_url(cm.CHECK_TPO_URL, 1)
            self.assertRaises(NoSuchElementException,
                              driver.find_element_by_link_text,
                              "JavaScript is enabled.")

    def test_security_slider_settings_low_mid(self):
        for sec_slider_setting in [2, 3, 4]:
            # 2: medium-high, 3: medium-low, 4: low (default)
            el = None
            sec_slider_pref = {"extensions.torbutton.security_slider":
                               sec_slider_setting}
            with TorBrowserDriver(TBB_PATH,
                                  pref_dict=sec_slider_pref) as driver:
                driver.load_url(cm.CHECK_TPO_URL, 1)
                el = driver.find_element_by_link_text("JavaScript is enabled.")
                self.assertTrue(el)

    def test_tbb_logfile(self):
        """Make sure log file is populated."""
        _, log_file = tempfile.mkstemp()
        log_len = len(read_file(log_file))
        self.assertEqual(log_len, 0)

        with TorBrowserDriver(TBB_PATH, tbb_logfile_path=log_file) as driver:
            driver.load_url(cm.CHECK_TPO_URL, 1)

        log_txt = read_file(log_file)
        self.assertTrue(len(log_txt))
        # make sure we find the expected strings in the log
        self.assertIn("torbutton@torproject.org", log_txt)
        self.assertIn("addons.manager", log_txt)
        if exists(log_file):
            remove(log_file)


class HTTPSEverywhereDisabledTest(unittest.TestCase):
    def test_https_everywhere_disabled(self):
        """Make sure the HTTP->HTTPS redirection in the
        test_httpseverywhere test is due to HTTPSEverywhere -
        not because the site is forwarding to HTTPS by default.
        """
        disable_HE_pref = {"extensions.https_everywhere.globalEnabled": False}
        with TorBrowserDriver(TBB_PATH, pref_dict=disable_HE_pref) as driver:
            driver.load_url(TEST_HTTP_URL, 1)
            err_msg = "Test should be updated to use a site that doesn't \
                auto-forward HTTP to HTTPS. %s " % driver.current_url
            self.failIfEqual(driver.current_url,  TEST_HTTPS_URL, err_msg)
            self.assertEqual(driver.current_url, TEST_HTTP_URL,
                             "Can't load the test page")
