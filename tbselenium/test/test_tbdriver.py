import sys
import tempfile
import pytest
import unittest
from os import remove, environ
from os.path import getsize, exists, join, dirname, isfile

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.utils import is_connectable

from tbselenium.exceptions import TBDriverPathError, TBDriverPortError
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TorBrowserDriverFixture as TBDriverFixture
from tbselenium.test.fixtures import launch_tor_with_config_fixture
import tbselenium.utils as ut

TEST_LONG_WAIT = 60

WEBGL_CHECK_JS = "var cvs = document.createElement('canvas');\
                    return cvs.getContext('experimental-webgl');"

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/marionette/tor_browser_tests/test_https-everywhere.py#n18
TEST_HTTP_URL = "http://www.freedomboxfoundation.org/thanks/"
TEST_HTTPS_URL = "https://www.freedomboxfoundation.org/thanks/"

MISSING_DIR = "_no_such_directory_"
MISSING_FILE = "_no_such_file_"

SEC_SLIDER_PREF = "extensions.torbutton.security_slider"


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDriverFixture(TBB_PATH)

    def tearDown(self):
        self.tb_driver.quit()

    def test_tbdriver_simple_visit(self):
        """check.torproject.org should detect Tor IP."""
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        self.tb_driver.find_element_by("h1.on")

    def test_tbdriver_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_path = join(TBB_PATH, cm.DEFAULT_TBB_PROFILE_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(profile_path)
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(profile_path)
        self.assertEqual(last_mod_time_before, last_mod_time_after)

    def test_httpseverywhere(self):
        """HTTPSEverywhere should redirect to HTTPS version."""
        self.tb_driver.load_url_ensure(TEST_HTTP_URL)
        WebDriverWait(self.tb_driver, TEST_LONG_WAIT).\
            until(EC.title_contains("thanks"))
        self.assertEqual(self.tb_driver.current_url, TEST_HTTPS_URL)

    def test_noscript(self):
        """NoScript should disable WebGL."""
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL,
                                       wait_for_page_body=True)
        webgl_support = self.tb_driver.execute_script(WEBGL_CHECK_JS)
        self.assertIsNone(webgl_support)

    def test_correct_firefox_binary(self):
        self.assertTrue(self.tb_driver.binary.which('firefox').
                        startswith(TBB_PATH))

    def test_should_load_tbb_firefox_libs(self):
        """Make sure we load the Firefox libraries from the TBB directories.
        We only test libxul (main Firefox/Gecko library) and libstdc++.
        """
        driver = self.tb_driver
        if sys.platform == 'win32':
            pytest.skip("This test doesn't support Windows")
        pid = self.tb_driver.binary.process.pid
        xul_lib_path = join(driver.tbb_browser_dir, "libxul.so")
        std_c_lib_path = join(driver.tbb_path, cm.DEFAULT_TOR_BINARY_DIR,
                              "libstdc++.so.6")
        for lib_path in [xul_lib_path, std_c_lib_path]:
            self.failUnless(isfile(lib_path))
            # We read the memory map of the process
            # http://man7.org/linux/man-pages/man5/proc.5.html
            proc_mem_map_file = "/proc/%d/maps" % (pid)
            self.assertTrue(isfile(proc_mem_map_file))
            for map_line in open(proc_mem_map_file).readlines():
                if lib_path in map_line:
                    break  # Found the loaded library in the memory map
            else:
                self.fail("Can't find the loaded lib: %s" % (xul_lib_path))


class TBDriverFailTest(unittest.TestCase):

    def test_should_raise_for_missing_paths(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TBDriverFixture()
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided ")

    def test_should_raise_for_missing_tbb_path(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TBDriverFixture(tbb_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "TBB path is not a directory %s" % MISSING_DIR)

    def test_should_raise_for_missing_fx_binary(self):
        temp_dir = tempfile.mkdtemp()
        with self.assertRaises(TBDriverPathError) as exc:
            TBDriverFixture(tbb_fx_binary_path=MISSING_FILE,
                            tbb_profile_path=temp_dir)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox binary %s" % MISSING_FILE)

    def test_should_raise_for_missing_fx_profile(self):
        _, temp_file = tempfile.mkstemp()
        with self.assertRaises(TBDriverPathError) as exc:
            TBDriverFixture(tbb_fx_binary_path=temp_file,
                            tbb_profile_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox profile dir %s" % MISSING_DIR)

    def test_should_raise_for_invalid_pref_dict(self):
        with self.assertRaises(AttributeError):
            TBDriverFixture(TBB_PATH, pref_dict="foo")
        with self.assertRaises(AttributeError):
            TBDriverFixture(TBB_PATH, pref_dict=[1, 2])
        with self.assertRaises(AttributeError):
            TBDriverFixture(TBB_PATH, pref_dict=(1, 2))

    def test_should_fail_launching_tor_on_custom_socks_port(self):
        with self.assertRaises(TBDriverPortError):
            TBDriverFixture(TBB_PATH, socks_port=10001,
                            tor_cfg=cm.LAUNCH_NEW_TBB_TOR)

    def test_should_not_load_with_wrong_sys_socks_port(self):
        with TBDriverFixture(TBB_PATH, socks_port=9999,
                             tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url(cm.CHECK_TPO_URL)
            self.assertTrue(driver.is_connection_error_page)


class ScreenshotTest(unittest.TestCase):
    def setUp(self):
        _, self.temp_file = tempfile.mkstemp()

    def tearDown(self):
        if exists(self.temp_file):
            remove(self.temp_file)

    def test_screen_capture(self):
        """Make sure we can capture the screen.
        Passing canvas_allowed_hosts is not needed for TBB >= 4.5a3
        """
        canvas_allowed = [cm.CHECK_TPO_HOST]
        with TBDriverFixture(TBB_PATH,
                             canvas_allowed_hosts=canvas_allowed) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, 3)
            driver.get_screenshot_as_file(self.temp_file)
        # A blank image for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture of the same page is ~57KB. If the capture
        # is not blank it should be at least greater than 20KB.
        self.assertGreater(getsize(self.temp_file), 20000)


class TBDriverOptionalArgs(unittest.TestCase):

    def test_add_ports_to_fx_banned_ports(self):
        test_socks_port = 9999
        # No Tor process is listening on 9999, we just test the pref
        with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                             socks_port=test_socks_port) as driver:
            for pref in cm.PORT_BAN_PREFS:
                banned_ports = driver.profile.default_preferences[pref]
                self.assertIn(str(test_socks_port), banned_ports)

    def test_running_with_system_tor(self):
        """Make sure we can run using the tor running on the system.
        This test requires a system tor process with SOCKS port 9050.
        """
        if not is_connectable(cm.DEFAULT_SOCKS_PORT):
            pytest.skip("Skipping. Start system Tor to run the test.")
        with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")

    def test_running_with_stem(self):
        """We should be able to run with a tor process started with Stem."""
        try:
            from stem.control import Controller
        except ImportError as err:
            pytest.skip("Can't import Stem. Skipping test: %s" % err)
        custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
        environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)
        # any port would do, pick 9250, 9251 to avoid conflict
        socks_port = 9250
        control_port = 9251
        temp_data_dir = tempfile.mkdtemp()
        torrc = {'ControlPort': str(control_port),
                 'SOCKSPort': str(socks_port),
                 'DataDirectory': temp_data_dir}
        tor_process = launch_tor_with_config_fixture(config=torrc,
                                                     tor_cmd=custom_tor_binary)
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                                 socks_port=socks_port) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("h1.on")

        # Kill tor process
        if tor_process:
            tor_process.kill()

    def test_tbb_logfile(self):
        """Make sure log file is populated."""
        _, log_file = tempfile.mkstemp()
        log_len = len(ut.read_file(log_file))
        self.assertEqual(log_len, 0)

        with TBDriverFixture(TBB_PATH, tbb_logfile_path=log_file) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)

        log_txt = ut.read_file(log_file)
        # make sure we find the expected strings in the log
        self.assertIn("torbutton@torproject.org", log_txt)
        self.assertIn("addons.manager", log_txt)
        if exists(log_file):
            remove(log_file)

    def test_temp_tor_data_dir(self):
        """If we use a temporary directory as tor_data_dir,
        tor datadir in TBB should stay unchanged.
        """
        tmp_dir = tempfile.mkdtemp()
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDriverFixture(TBB_PATH, tor_data_dir=tmp_dir) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertEqual(last_mod_time_before, last_mod_time_after)

    def test_non_temp_tor_data_dir(self):
        """Tor data dir in TBB should change if we don't use tor_data_dir."""
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertNotEqual(last_mod_time_before, last_mod_time_after)


class TBSecuritySlider(unittest.TestCase):

    def test_security_slider_settings_hi(self):
        """Setting `High` should disable JavaScript."""
        with TBDriverFixture(TBB_PATH,
                             pref_dict={SEC_SLIDER_PREF: 1}) as driver:
            if not driver.supports_sec_slider:
                pytest.skip("Security slider is not supported")
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security slider should disable JavaScript")
            except (NoSuchElementException, TimeoutException):
                pass

    def test_security_slider_settings_low_mid(self):
        # TODO: test other features to distinguish between levels
        for sec_slider_setting in [2, 3, 4]:
            slider_dict = {SEC_SLIDER_PREF: sec_slider_setting}
            # 2: medium-high, 3: medium-low, 4: low (default)
            with TBDriverFixture(TBB_PATH, pref_dict=slider_dict) as driver:
                if not driver.supports_sec_slider:
                    pytest.skip("Security slider is not supported")
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)


class TBDriverTestAssumptions(unittest.TestCase):
    """Tests for some assumptions we use in the above tests."""
    def test_https_everywhere_disabled(self):
        """Make sure the HTTP->HTTPS redirection in the
        test_httpseverywhere test is due to HTTPSEverywhere -
        not because the site is forwarding to HTTPS by default.
        """
        disable_HE_pref = {"extensions.https_everywhere.globalEnabled": False}
        with TBDriverFixture(TBB_PATH, pref_dict=disable_HE_pref) as driver:
            driver.load_url_ensure(TEST_HTTP_URL, 1)
            err_msg = "Test should be updated to use a site that doesn't \
                auto-forward HTTP to HTTPS. %s " % driver.current_url
            self.failIfEqual(driver.current_url, TEST_HTTPS_URL, err_msg)
            self.assertEqual(driver.current_url, TEST_HTTP_URL,
                             "Can't load the test page")

    def test_noscript_webgl_enabled(self):
        """Make sure that when we disable NoScript's WebGL blocking,
        WebGL becomes available. This is to the test method we
        use in test_noscript is sane.
        """
        disable_NS_webgl_pref = {"noscript.forbidWebGL": False}
        with TBDriverFixture(TBB_PATH,
                             pref_dict=disable_NS_webgl_pref) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, wait_for_page_body=True)
            webgl_support = driver.execute_script(WEBGL_CHECK_JS)
            self.assertIsNotNone(webgl_support)
            self.assertIn("activeTexture", webgl_support)
            self.assertIn("getSupportedExtensions", webgl_support)
