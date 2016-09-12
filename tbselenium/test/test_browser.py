import pytest
import sys
import unittest
import psutil
import tempfile
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test.process_utils import get_fx_proc_from_geckodriver_service
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.utils import read_file
from os.path import exists, getmtime, join
from os import remove


class TorBrowserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if cm.GECKODRIVER_FIXED_LOGFILE_ISSUE:
            cls.log_file = join(TBB_PATH, cm.DEFAULT_TBB_BROWSER_DIR,
                                "geckodriver.log")
        else:
            _, cls.log_file = tempfile.mkstemp()
        cls.driver = TBDriverFixture(TBB_PATH, tbb_logfile_path=cls.log_file)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        if exists(cls.log_file):
            remove(cls.log_file)

    def test_correct_firefox_binary(self):
        self.assertTrue(self.driver.binary.which('firefox').
                        startswith(TBB_PATH))

    def test_tbb_logfile(self):
        log_txt = read_file(self.log_file)
        self.assertIn("torbutton@torproject.org", log_txt)
        self.assertIn("addons.manager", log_txt)

    @pytest.mark.skipif(sys.platform != 'linux2', reason='Requires Linux')
    def test_should_load_tbb_firefox_libs(self):
        """Make sure we load the Firefox libraries from the TBB directories.
        We only test libxul (main Firefox/Gecko library) and libstdc++.

        """
        found_xul_lib = False
        found_std_c_lib = False
        driver = self.driver
        xul_lib_path = join(driver.tbb_browser_dir, "libxul.so")
        std_c_lib_path = join(driver.tbb_path, cm.DEFAULT_TOR_BINARY_DIR,
                              "libstdc++.so.6")
        if driver.capabilities.get("marionette"):
            tb_proc = get_fx_proc_from_geckodriver_service(driver)
        else:
            tb_proc = psutil.Process(driver.binary.process.pid)

        for pmap in tb_proc.memory_maps():
            if "libxul.so" in pmap.path:
                self.assertEqual(xul_lib_path, pmap.path)
                found_xul_lib = True
            elif "libstdc++.so.6" in pmap.path:
                self.assertEqual(std_c_lib_path, pmap.path)
                found_std_c_lib = True
        self.assertTrue(found_xul_lib)
        self.assertTrue(found_std_c_lib)

    def test_tbdriver_fx_profile_not_be_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_path = join(TBB_PATH, cm.DEFAULT_TBB_PROFILE_PATH)
        mtime_before = getmtime(profile_path)
        self.driver.load_url_ensure(cm.CHECK_TPO_URL)
        mtime_after = getmtime(profile_path)
        self.assertEqual(mtime_before, mtime_after)
