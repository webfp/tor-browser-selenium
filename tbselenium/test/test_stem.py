import unittest
import pytest
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test.fixtures import launch_tbb_tor_with_stem_fixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH

try:
    from stem.control import Controller
except ImportError as err:
    pytest.skip("Can't import Stem. Skipping test: %s" % err)


class TBStemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TBStemTest, cls).setUpClass()
        cls.tor_process = launch_tbb_tor_with_stem_fixture(tbb_path=TBB_PATH)
        cls.controller = Controller.from_port(port=cm.STEM_CONTROL_PORT)
        cls.controller.authenticate()
        cls.driver = TBDriverFixture(TBB_PATH,
                                     tor_cfg=cm.USE_RUNNING_TOR,
                                     socks_port=cm.STEM_SOCKS_PORT,
                                     control_port=cm.STEM_CONTROL_PORT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.controller.close()
        if cls.tor_process:
            cls.tor_process.kill()

    def test_should_add_custom_ports_to_fx_banned_ports(self):
        for pref in cm.PORT_BAN_PREFS:
            banned_ports = self.driver.profile.default_preferences[pref]
            self.assertIn(str(cm.STEM_SOCKS_PORT), banned_ports)
            self.assertIn(str(cm.STEM_CONTROL_PORT), banned_ports)

    def test_running_with_stem(self):
        driver = self.driver
        driver.load_url_ensure(cm.CHECK_TPO_URL)
        driver.find_element_by("h1.on")
        ccts = self.controller.get_circuits()
        self.assertGreater(len(ccts), 0)

if __name__ == "__main__":
    unittest.main()
