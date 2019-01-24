import unittest
import pytest
import tempfile
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test.fixtures import launch_tbb_tor_with_stem_fixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from selenium.webdriver.common.utils import free_port

try:
    from stem.control import Controller
except ImportError as err:
    pytest.skip("Can't import Stem. Skipping test: %s" % err)


class TBStemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TBStemTest, cls).setUpClass()
        cls.control_port = free_port()
        cls.socks_port = free_port()
        temp_data_dir = tempfile.mkdtemp()
        torrc = {'ControlPort': str(cls.control_port),
                 'SOCKSPort': str(cls.socks_port),
                 'DataDirectory': temp_data_dir}
        cls.tor_process = launch_tbb_tor_with_stem_fixture(tbb_path=TBB_PATH,
                                                           torrc=torrc)
        cls.controller = Controller.from_port(port=cls.control_port)
        cls.controller.authenticate()
        cls.driver = TBDriverFixture(TBB_PATH,
                                     tor_cfg=cm.USE_STEM,
                                     socks_port=cls.socks_port,
                                     control_port=cls.control_port)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.controller.close()
        if cls.tor_process:
            cls.tor_process.kill()

    def test_should_add_custom_ports_to_fx_banned_ports(self):
        for pref in cm.PORT_BAN_PREFS:
            banned_ports = self.driver.profile.default_preferences[pref]
            self.assertIn(str(self.socks_port), banned_ports)
            self.assertIn(str(self.control_port), banned_ports)

    def test_running_with_stem(self):
        driver = self.driver
        driver.load_url_ensure(cm.CHECK_TPO_URL)
        driver.find_element_by("h1.on")
        ccts = self.controller.get_circuits()
        self.assertGreater(len(ccts), 0)


if __name__ == "__main__":
    unittest.main()
