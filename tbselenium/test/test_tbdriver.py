import tempfile
import pytest
import unittest
from os.path import join

from selenium.webdriver.common.utils import is_connectable

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
import tbselenium.utils as ut


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
        if not is_connectable(cm.DEFAULT_SOCKS_PORT):
            pytest.skip("Skipping. Start system Tor to run the test.")
        with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")

    def test_temp_tor_data_dir(self):
        """If we use a temporary directory as tor_data_dir,
        tor datadir in TBB should remain unchanged.
        """

        tmp_dir = tempfile.mkdtemp()
        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDriverFixture(TBB_PATH,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR,
                             tor_data_dir=tmp_dir) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertEqual(last_mod_time_before, last_mod_time_after)

    def test_non_temp_tor_data_dir(self):
        """Tor data dir in TBB should be modified if we don't use a temporary
        tor_data_dir.
        """

        tbb_tor_data_path = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)
        last_mod_time_before = ut.get_last_modified_of_dir(tbb_tor_data_path)
        with TBDriverFixture(TBB_PATH,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        last_mod_time_after = ut.get_last_modified_of_dir(tbb_tor_data_path)
        self.assertNotEqual(last_mod_time_before, last_mod_time_after)
