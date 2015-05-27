import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import common as cm
from utils import get_hash_of_directory
from datacollection.torutils import TorBrowserDriver
from datacollection.torutils import TorController

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere.js
HTTP_URL = "http://www.mediawiki.org/wiki/MediaWiki"
HTTPS_URL = "https://www.mediawiki.org/wiki/MediaWiki"


class TestTorUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tor_controller = TorController(cm.TORRC_WANG_AND_GOLDBERG,
                                           cm.TBB_DEFAULT_VERSION)
        cls.tor_process = cls.tor_controller.launch_tor_service()

    def test_launch_tor_service(self):
        self.tor_process.kill()
        self.tor_process = self.tor_controller.launch_tor_service()
        self.assertTrue(self.tor_process, 'Cannot launch Tor process')

    def test_tb_orig_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        tbb_profile_dir = cm.get_tbb_profile_path(cm.TBB_DEFAULT_VERSION)
        profile_hash_before = get_hash_of_directory(tbb_profile_dir)
        tb_driver = TorBrowserDriver()
        tb_driver.get("http://check.torproject.org")
        tb_driver.quit()
        profile_hash_after = get_hash_of_directory(tbb_profile_dir)
        assert(profile_hash_after == profile_hash_before)

    def test_tb_drv_simple_visit(self):
        tb_driver = TorBrowserDriver()
        tb_driver.get("http://check.torproject.org")
        tb_driver.implicitly_wait(60)
        h1_on = tb_driver.find_element_by_css_selector("h1.on")
        self.assertTrue(h1_on)
        tb_driver.quit()

    def test_tb_extensions(self):
        tb_driver = TorBrowserDriver()
        # test HTTPS Everywhere
        tb_driver.get(HTTP_URL)
        time.sleep(1)
        try:
            WebDriverWait(tb_driver, 60).until(
                EC.title_contains("MediaWiki")
            )
        except TimeoutException:
            self.fail("The title should contain MediaWiki")
        self.assertEqual(tb_driver.current_url, HTTPS_URL)
        # NoScript should disable WebGL
        webgl_test_url = "https://developer.mozilla.org/samples/webgl/sample1/index.html"  # noqa
        tb_driver.get(webgl_test_url)
        try:
            WebDriverWait(tb_driver, 60).until(
                EC.alert_is_present()
            )
        except TimeoutException:
            self.fail("WebGL error alert should be present")
        tb_driver.switch_to_alert().dismiss()
        tb_driver.implicitly_wait(30)
        el = tb_driver.find_element_by_class_name("__noscriptPlaceholder__")
        self.assertTrue(el)
        # sanity check for the above test
        self.assertRaises(NoSuchElementException,
                          tb_driver.find_element_by_class_name,
                          "__nosuch_class_exist")
        tb_driver.quit()

    def test_https_everywhere_disabled(self):
        """Test to make sure the HTTP->HTTPS redirection observed in the

        previous test (test_tb_extensions) is really due to HTTPSEverywhere -
        but not because the site is HTTPS by default. See, the following:
        https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere-disabled.js
        """

        ff_driver = webdriver.Firefox()
        ff_driver.get(HTTP_URL)
        time.sleep(1)
        # make sure it doesn't redirect to https
        self.assertEqual(ff_driver.current_url, HTTP_URL)
        ff_driver.quit()

    def test_close_all_streams(self):
        streams_open = False
        new_tb_drv = TorBrowserDriver()
        new_tb_drv.get('http://www.google.com')
        time.sleep(cm.WAIT_IN_SITE)
        self.tor_controller.close_all_streams()
        for stream in self.tor_controller.controller.get_streams():
            print stream.id, stream.purpose, stream.target_address, "open!"
            streams_open = True
        new_tb_drv.quit()
        self.assertFalse(streams_open, 'Could not close all streams.')

    @classmethod
    def tearDownClass(cls):
        # cls.tor_process.kill()
        cls.tor_controller.kill_tor_proc()

if __name__ == "__main__":
    unittest.main()
