import pytest
import sys
import unittest
import tempfile
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
import tbselenium.utils as ut

from os.path import exists, join
from os import remove


class TorBrowserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        log_txt = ut.read_file(self.log_file)
        self.assertIn("torbutton@torproject.org", log_txt)
        self.assertIn("addons.manager", log_txt)

    @pytest.mark.skipif(sys.platform != 'linux2', reason='Requires Linux')
    def test_should_load_tbb_firefox_libs(self):
        """Make sure we load the Firefox libraries from the TBB directories.
        We only test libxul (main Firefox/Gecko library) and libstdc++.

        The memory map of the TB process is used to find loaded libraries.
        http://man7.org/linux/man-pages/man5/proc.5.html
        """

        driver = self.driver
        pid = driver.binary.process.pid
        xul_lib_path = join(driver.tbb_browser_dir, "libxul.so")
        std_c_lib_path = join(driver.tbb_path, cm.DEFAULT_TOR_BINARY_DIR,
                              "libstdc++.so.6")
        proc_mem_map_file = "/proc/%d/maps" % (pid)
        mem_map = ut.read_file(proc_mem_map_file)
        self.assertIn(xul_lib_path, mem_map)
        self.assertIn(std_c_lib_path, mem_map)

    def test_tbdriver_fx_profile_not_be_modified(self):
        """Visiting a site should not modify the original profile contents."""
        profile_path = join(TBB_PATH, cm.DEFAULT_TBB_PROFILE_PATH)
        mtime_before = ut.get_dir_mtime(profile_path)
        self.driver.load_url_ensure(cm.CHECK_TPO_URL)
        mtime_after = ut.get_dir_mtime(profile_path)
        self.assertEqual(mtime_before, mtime_after)
