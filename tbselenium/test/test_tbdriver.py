import re
import sys
import tempfile
import pytest
import unittest
from os import remove, environ
from os.path import getsize, exists, join, dirname, isfile
from distutils.version import LooseVersion

from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.utils import is_connectable

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TorBrowserDriverFixture as TBDTestFixture
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


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDTestFixture(TBB_PATH)

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

    @pytest.mark.skipif(sys.platform == 'win32',
                        reason="Test does not support Windows")
    def test_should_load_tbb_firefox_libs(self):
        """Make sure we load the Firefox libraries from the TBB directories.
        We only test libxul (main Firefox/Gecko library) and libstdc++.
        """
        xul_lib_path = join(self.tb_driver.tbb_browser_dir, "libxul.so")
        std_c_lib_path = join(self.tb_driver.tbb_path,
                              cm.DEFAULT_TOR_BINARY_DIR,
                              "libstdc++.so.6")

        self.failUnless(self.tb_driver.binary.process,
                        "TorBrowserDriver process doesn't exist")
        pid = self.tb_driver.binary.process.pid

        for lib_path in [xul_lib_path, std_c_lib_path]:
            self.failUnless(isfile(lib_path),
                            "Can't find the library %s" % lib_path)
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
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TBDTestFixture()
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided ")

    def test_should_raise_for_missing_tbb_path(self):
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TBDTestFixture(tbb_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "TBB path is not a directory %s" % MISSING_DIR)

    def test_should_raise_for_missing_fx_binary(self):
        temp_dir = tempfile.mkdtemp()
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TBDTestFixture(tbb_fx_binary_path=MISSING_FILE,
                           tbb_profile_path=temp_dir)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox binary %s" % MISSING_FILE)

    def test_should_raise_for_missing_fx_profile(self):
        _, temp_file = tempfile.mkstemp()
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TBDTestFixture(tbb_fx_binary_path=temp_file,
                           tbb_profile_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox profile dir %s" % MISSING_DIR)

    def test_should_raise_for_invalid_pref_dict(self):
        with self.assertRaises(AttributeError):
            TBDTestFixture(TBB_PATH, pref_dict="foo")
        with self.assertRaises(AttributeError):
            TBDTestFixture(TBB_PATH, pref_dict=[1, 2])
        with self.assertRaises(AttributeError):
            TBDTestFixture(TBB_PATH, pref_dict=(1, 2))

    def test_should_fail_launching_tor_on_custom_socks_port(self):
        with self.assertRaises(cm.TBDriverPortError):
            TBDTestFixture(TBB_PATH, socks_port=10001,
                           tor_cfg=cm.LAUNCH_NEW_TBB_TOR)

    def test_should_not_load_with_wrong_sys_socks_port(self):
        with TBDTestFixture(TBB_PATH, socks_port=9999,
                            tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url(cm.CHECK_TPO_URL)
            self.assertTrue(driver.is_connection_error_page())


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
        with TBDTestFixture(TBB_PATH,
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
        with TBDTestFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                            socks_port=test_socks_port) as driver:
            for pref in cm.PORT_BAN_PREFS:
                banned_ports = driver.profile.default_preferences[pref]
                self.assertIn(str(test_socks_port), banned_ports)

    def test_running_with_system_tor(self):
        """Make sure we can run using the tor running on the system.
        This test requires a system tor process with SOCKS port 9050.
        """
        if not is_connectable(cm.DEFAULT_SOCKS_PORT):
            print("Skipping system tor test. Start tor to run this test.")
            return
        with TBDTestFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")

    def test_running_with_stem(self):
        """We should be able to run with a tor process started with Stem."""
        try:
            from stem.control import Controller
        except ImportError as err:
            print("Can't import Stem. Skipping test: %s" % err)
            return
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
            with TBDTestFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                                socks_port=socks_port) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("h1.on")

        # Kill tor process
        if tor_process:
            tor_process.kill()

    def test_security_slider_settings_hi(self):
        slider_pref = {"extensions.torbutton.security_slider": 1}
        with TBDTestFixture(TBB_PATH, pref_dict=slider_pref) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, 1)
            self.assertRaises(NoSuchElementException,
                              driver.find_element_by_link_text,
                              "JavaScript is enabled.")

    def test_security_slider_settings_low_mid(self):
        for sec_slider_setting in [2, 3, 4]:
            # 2: medium-high, 3: medium-low, 4: low (default)
            el = None
            slider_pref = {"extensions.torbutton.security_slider":
                           sec_slider_setting}
            with TBDTestFixture(TBB_PATH,
                                pref_dict=slider_pref) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                try:
                    el = driver.find_element_by("JavaScript is enabled.",
                                                find_by=By.LINK_TEXT)
                except TimeoutException:
                    self.fail("Can't confirm if JS is enabled for security "
                              "slider setting %s, on page %s."
                              % (sec_slider_setting, driver.title))
                self.assertTrue(el)

    def test_tbb_logfile(self):
        """Make sure log file is populated."""
        _, log_file = tempfile.mkstemp()
        log_len = len(ut.read_file(log_file))
        self.assertEqual(log_len, 0)

        with TBDTestFixture(TBB_PATH, tbb_logfile_path=log_file) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)

        log_txt = ut.read_file(log_file)
        # make sure we find the expected strings in the log
        self.assertIn("torbutton@torproject.org", log_txt)
        self.assertIn("addons.manager", log_txt)
        if exists(log_file):
            remove(log_file)

    def test_font_bundling(self):
        _, log_file = tempfile.mkstemp()
        used_font_files = set()
        bundled_fonts_dir = join(TBB_PATH, cm.DEFAULT_BUNDLED_FONTS_PATH)
        bundled_fonts_dir = bundled_fonts_dir
        # https://www.freedesktop.org/software/fontconfig/fontconfig-user.html
        environ["FC_DEBUG"] = "%d" % (1024 + 8 + 1)
        with TBDTestFixture(TBB_PATH, tbb_logfile_path=log_file) as driver:
            driver.load_url_ensure("about:tor")
            ver = ut.get_tbb_version(driver.page_source)
            if not ver or (LooseVersion(ver) <= LooseVersion('4.5')):
                print ("TBB version doesn't support font bundling %s" % ver)
                return
            driver.load_url_ensure("https://www.wikipedia.org/")

        bundled_font_files = set(ut.gen_find_files(bundled_fonts_dir))
        self.assertTrue(len(bundled_font_files) > 0)
        log_txt = ut.read_file(log_file)

        fonts_conf_path = join(TBB_PATH, cm.DEFAULT_FONTS_CONF_PATH)
        expected_log = "Loading config file %s" % fonts_conf_path
        self.assertIn(expected_log, log_txt)

        # We get the following log if Firefox cannot find any fonts at startup
        self.assertNotIn("failed to choose a font, expect ugly output",
                         log_txt)

        expected_load_fonts_log = "adding fonts from%s" % bundled_fonts_dir
        self.assertIn(expected_load_fonts_log, log_txt)

        for _, font_path, _ in re.findall(r"(file: \")(.*)(\".*)", log_txt):
            # fontconfig logs include path to the font file, e.g.
            # file: "/path/to/tbb/Browser/fonts/Arimo-Bold.ttf"(w)
            self.assertIn(bundled_fonts_dir, font_path)
            used_font_files.add(font_path)
        # make sure the TBB only loaded and used the bundled fonts
        self.assertEqual(used_font_files, bundled_font_files)

    def test_temp_tor_data_dir(self):
        """If we use a temporary directory as tor_data_dir,
        tor datadir in TBB should stay unchanged.
        """
        tmp_dir = tempfile.mkdtemp()
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDTestFixture(TBB_PATH, tor_data_dir=tmp_dir) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertEqual(last_mod_time_before, last_mod_time_after)

    def test_non_temp_tor_data_dir(self):
        """Tor data dir in TBB should change if we don't use tor_data_dir."""
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDTestFixture(TBB_PATH) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertNotEqual(last_mod_time_before, last_mod_time_after)


class TBDriverTestAssumptions(unittest.TestCase):
    """Tests for some assumptions we use in the above tests."""
    def test_https_everywhere_disabled(self):
        """Make sure the HTTP->HTTPS redirection in the
        test_httpseverywhere test is due to HTTPSEverywhere -
        not because the site is forwarding to HTTPS by default.
        """
        disable_HE_pref = {"extensions.https_everywhere.globalEnabled": False}
        with TBDTestFixture(TBB_PATH, pref_dict=disable_HE_pref) as driver:
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
        with TBDTestFixture(TBB_PATH,
                            pref_dict=disable_NS_webgl_pref) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, wait_for_page_body=True)
            webgl_support = driver.execute_script(WEBGL_CHECK_JS)
            self.assertIsNotNone(webgl_support)
            self.assertIn("activeTexture", webgl_support)
            self.assertIn("getSupportedExtensions", webgl_support)
