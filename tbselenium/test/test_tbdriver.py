import tempfile
import unittest
import re
from os import remove, environ
from os.path import getsize, exists, join, abspath, dirname, isfile, basename

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tbselenium import common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH
import tbselenium.utils as ut
from tld.exceptions import TldBadUrl

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
        for _ in range(3):
            try:
                self.tb_driver = TorBrowserDriver(TBB_PATH)
                break
            except TimeoutException, exc:
                continue
        else:
            raise exc

    def tearDown(self):
        self.tb_driver.quit()

    def test_tbdriver_simple_visit(self):
        """check.torproject.org should detect Tor IP."""
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        self.tb_driver.find_element_by("h1.on")

    def test_tbdriver_profile_not_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_path = join(TBB_PATH, cm.DEFAULT_TBB_PROFILE_PATH)
        profile_hash_before = ut.get_hash_of_directory(profile_path)
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        profile_hash_after = ut.get_hash_of_directory(profile_path)
        self.assertEqual(profile_hash_before, profile_hash_after)

    def test_httpseverywhere(self):
        """HTTPSEverywhere should redirect to HTTPS version."""
        self.tb_driver.load_url_ensure(TEST_HTTP_URL)
        try:
            WebDriverWait(self.tb_driver, TEST_LONG_WAIT).\
                until(EC.title_contains("thanks"))
        except TimeoutException:
            self.fail("Can't find expected title %s" % self.tb_driver.title)
        self.assertEqual(self.tb_driver.current_url, TEST_HTTPS_URL)

    def test_noscript(self):
        """NoScript should disable WebGL."""
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL,
                                       wait_for_page_body=True)
        webgl_support = self.tb_driver.execute_script(WEBGL_CHECK_JS)
        self.assertIsNone(webgl_support)

    def test_should_load_tbb_firefox_libs(self):
        """Make sure we load the Firefox libraries from the TBB directories.

        We only test libxul (main Firefox/Gecko library) and libstdc++.
        """
        xul_lib_path = abspath(join(self.tb_driver.tbb_browser_dir,
                                    "libxul.so"))
        std_c_lib_path = abspath(join(self.tb_driver.tbb_path,
                                      cm.DEFAULT_TOR_BINARY_DIR,
                                      "libstdc++.so.6"))

        self.failUnless(self.tb_driver.binary.process,
                        "TorBrowserDriver process doesn't exist")
        pid = self.tb_driver.binary.process.pid

        for lib_path in [xul_lib_path, std_c_lib_path]:
            lib_loaded_from_tbb = False
            self.failUnless(isfile(lib_path),
                            "Can't find the library %s" % lib_path)
            lib_name = basename(lib_path)
            lib_escaped = lib_name.replace(".", "\.")  # to use with grep

            cmd = "lsof -p %d | awk '{print $9}' | grep '%s'"\
                % (pid, lib_escaped)
            status, out = ut.run_cmd(cmd)
            self.assertFalse(int(status),
                             "Error running command: %s\nStatus: %s\nOut: %s" %
                             (cmd, status, out))
            for out_line in out.split("\n"):
                if lib_name in out_line:  # remove potential lsof warning msgs
                    if lib_path == out_line:
                        lib_loaded_from_tbb = True

            self.assertTrue(lib_loaded_from_tbb,
                            "Can't find the loaded lib: %s\nCmd output: %s" %
                            (xul_lib_path, out))


class TBDriverFailTest(unittest.TestCase):

    def test_should_raise_for_missing_paths(self):
        with self.assertRaises(cm.TBDriverPathError) as exc:
            TorBrowserDriver()
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided ")

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

    def test_should_fail_with_wrong_sys_socks_port(self):
        with TorBrowserDriver(TBB_PATH, socks_port=9999,
                              tor_cfg=cm.USE_RUNNING_TOR) as driver:
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
            driver.load_url_ensure(cm.CHECK_TPO_URL, 3)
            driver.get_screenshot_as_file(self.temp_file)
        # A blank image for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture of the same page is ~57KB. If the capture
        # is not blank it should be at least greater than 20KB.
        self.assertGreater(getsize(self.temp_file), 20000)
        self.assertTrue(ut.is_png(self.temp_file),
                        "Doesn't look like a PNG file")


class TBDriverOptionalArgs(unittest.TestCase):

    def test_running_with_system_tor(self):
        """Make sure we can run using the tor running on the system.
        This test requires a system tor process with SOCKS port 9050.
        """
        if not ut.is_port_listening(cm.DEFAULT_SOCKS_PORT):
            print("Skipping system tor test. Start tor to run this test.")
            return
        with TorBrowserDriver(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")

    def test_running_with_stem(self):
        """We should be able to run with a tor process started with Stem."""
        try:
            from stem.control import Controller
            from stem.process import launch_tor_with_config
        except ImportError as err:
            print("Skipping Stem test. Install stem to run this test: %s" %
                  err)
            return
        custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
        environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)
        # any port number would do, pick 9250 to avoid conflict
        socks_port = cm.TBB_SOCKS_PORT
        control_port = cm.TBB_CONTROL_PORT
        temp_data_dir = tempfile.mkdtemp()
        torrc = {'ControlPort': str(control_port),
                 'SOCKSPort': str(socks_port),
                 'DataDirectory': temp_data_dir}
        tor_process = launch_tor_with_config(config=torrc,
                                             tor_cmd=custom_tor_binary)
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            with TorBrowserDriver(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                                  socks_port=socks_port) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("h1.on")

        # Kill tor process
        if tor_process:
            tor_process.kill()

    def test_security_slider_settings_hi(self):
        slider_pref = {"extensions.torbutton.security_slider": 1}
        with TorBrowserDriver(TBB_PATH, pref_dict=slider_pref) as driver:
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
            with TorBrowserDriver(TBB_PATH,
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

        with TorBrowserDriver(TBB_PATH, tbb_logfile_path=log_file) as driver:
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
        # join returns a relative path on Travis CI
        bundled_fonts_dir = abspath(bundled_fonts_dir)
        environ["FC_DEBUG"] = "%d" % (1024 + 8 + 1)
        """
        We set FC_DEBUG to 1024 + 8 + 1 to make sure we get logs about...
        MATCH            1    Brief information about font matching
        FONTSET          8    Track loading of font information at startup
        CONFIG        1024    Monitor which config files are loaded
        https://www.freedesktop.org/software/fontconfig/fontconfig-user.html
        """
        with TorBrowserDriver(TBB_PATH, tbb_logfile_path=log_file) as driver:
            driver.load_url_ensure("https://www.wikipedia.org/")
        bundled_font_files = set(ut.gen_find_files(bundled_fonts_dir))
        # make sure we discovered the bundled fonts
        self.assertTrue(len(bundled_font_files) > 0)
        log_txt = ut.read_file(log_file)

        expected_load_cfg_log = "Loading config file %s" %\
                                join(TBB_PATH, cm.DEFAULT_FONTS_CONF_PATH)
        self.assertIn(expected_load_cfg_log, log_txt)

        expected_load_fonts_log = "adding fonts from%s" % bundled_fonts_dir
        self.assertIn(expected_load_fonts_log, log_txt)

        # We get the following log if Firefox cannot find any fonts at startup
        #     (firefox:5611): Pango-WARNING **: failed to choose a font, expect ugly output. engine-type='PangoRenderFc', script='common'  # noqa
        self.assertNotIn("failed to choose a font, expect ugly output",
                         log_txt)
        for _, font_path, _ in re.findall(r"(file: \")(.*)(\".*)", log_txt):
            # make sure all fonts are loaded from the bundled font directory
            # fontconfig logs include path to the font file, e.g.
            # file: "/path/to/tbb/Browser/fonts/Arimo-Bold.ttf"(w)
            self.assertIn(bundled_fonts_dir, font_path)
            used_font_files.add(font_path)
        # make sure the TBB only loaded and used the bundled fonts
        self.assertEqual(used_font_files, bundled_font_files)
        environ["FC_DEBUG"] = ""

    def test_correct_firefox_binary(self):
        with TorBrowserDriver(TBB_PATH) as driver:
            self.assertTrue(driver.binary.which('firefox').
                            startswith(TBB_PATH))

    def test_temp_tor_data_dir(self):
        """If we use a temporary directory as tor_data_dir,
        tor datadir in TBB should stay unchanged.
        """
        tmp_dir = tempfile.mkdtemp()
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        hash_before = ut.get_hash_of_directory(tbb_tor_data_path)
        with TorBrowserDriver(TBB_PATH, tor_data_dir=tmp_dir) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        hash_after = ut.get_hash_of_directory(tbb_tor_data_path)
        self.assertEqual(hash_before, hash_after)

    def test_non_temp_tor_data_dir(self):
        """Tor data dir in TBB should change if we don't use tor_data_dir."""
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        hash_before = ut.get_hash_of_directory(tbb_tor_data_path)
        with TorBrowserDriver(TBB_PATH) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        hash_after = ut.get_hash_of_directory(tbb_tor_data_path)
        self.assertNotEqual(hash_before, hash_after)


class TBDriverTestAssumptions(unittest.TestCase):
    """Tests for some assumptions we use in the above tests."""
    def test_https_everywhere_disabled(self):
        """Make sure the HTTP->HTTPS redirection in the
        test_httpseverywhere test is due to HTTPSEverywhere -
        not because the site is forwarding to HTTPS by default.
        """
        disable_HE_pref = {"extensions.https_everywhere.globalEnabled": False}
        with TorBrowserDriver(TBB_PATH, pref_dict=disable_HE_pref) as driver:
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
        with TorBrowserDriver(TBB_PATH,
                              pref_dict=disable_NS_webgl_pref) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL, wait_for_page_body=True)
            webgl_support = driver.execute_script(WEBGL_CHECK_JS)
            self.assertIsNotNone(webgl_support)
            self.assertIn("activeTexture", webgl_support)
            self.assertIn("getSupportedExtensions", webgl_support)
