import tempfile
import unittest
import pytest
from os import environ
from os.path import join, isdir, getmtime

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDriverFixture(TBB_PATH)

    def tearDown(self):
        self.tb_driver.quit()

    def test_should_load_check_tpo(self):
        congrats = "Congratulations. This browser is configured to use Tor."
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        status = self.tb_driver.find_element_by("h1.on")
        self.assertEqual(status.text, congrats)

    def test_should_load_hidden_service(self):
        self.tb_driver.load_url_ensure("http://3g2upl4pq6kufc4m.onion")
        self.assertIn("DuckDuckGo", self.tb_driver.title)

    def test_should_check_environ_in_prepend(self):
        self.tb_driver.quit()
        self.tb_driver = TBDriverFixture(TBB_PATH)
        paths = environ["PATH"].split(':')
        tbbpath_count = paths.count(self.tb_driver.tbb_browser_dir)
        self.assertEqual(tbbpath_count, 1)


class TBDriverCleanUp(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDriverFixture(TBB_PATH)

    def test_browser_process_should_be_terminated_after_quit(self):
        driver = self.tb_driver
        if driver.capabilities.get("marionette"):
            fx_process = driver.service.process
        else:
            fx_process = driver.binary.process

        self.assertEqual(fx_process.poll(), None)
        driver.quit()
        self.assertNotEqual(fx_process.poll(), None)

    def test_profile_dirs_should_be_removed(self):
        driver = self.tb_driver
        tempfolder = driver.profile.tempfolder
        profile_path = driver.profile.path

        self.assertTrue(isdir(tempfolder))
        self.assertTrue(isdir(profile_path))
        driver.quit()
        self.assertFalse(isdir(profile_path))
        self.assertFalse(isdir(tempfolder))


class TBDriverTorDataDir(unittest.TestCase):

    TOR_DATA_PATH = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)

    @pytest.mark.skipif(cm.TRAVIS, reason="Requires Tor bootstrap,"
                        "unreliable on Travis")
    def test_temp_tor_data_dir(self):
        """Tor data directory in TBB should not be modified if
        we use a separate tor_data_dir.
        """
        tmp_dir = tempfile.mkdtemp()
        mod_time_before = getmtime(self.TOR_DATA_PATH)

        with TBDriverFixture(TBB_PATH, tor_data_dir=tmp_dir,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        mod_time_after = getmtime(self.TOR_DATA_PATH)
        self.assertEqual(mod_time_before, mod_time_after)

    @pytest.mark.skipif(cm.TRAVIS, reason="Requires Tor bootstrap,"
                        "unreliable on Travis")
    def test_non_temp_tor_data_dir(self):
        """Tor data directory in TBB should be modified if we don't
        use a separate tor_data_dir.
        """
        mod_time_before = getmtime(self.TOR_DATA_PATH)

        with TBDriverFixture(TBB_PATH,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        mod_time_after = getmtime(self.TOR_DATA_PATH)
        self.assertNotEqual(mod_time_before, mod_time_after)
