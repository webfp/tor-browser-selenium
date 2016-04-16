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

    def tearDown(self):
        if self.tor_process:
            self.tor_process.kill()

    def test_running_with_stem(self):
        self.tor_process = launch_tbb_tor_with_stem_fixture()
        with Controller.from_port(port=cm.STEM_CONTROL_PORT) as controller:
            controller.authenticate()

            with TBDriverFixture(TBB_PATH,
                                 tor_cfg=cm.USE_RUNNING_TOR,
                                 socks_port=cm.STEM_SOCKS_PORT) as driver:

                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("h1.on")
                ccts = controller.get_circuits()
                self.assertGreater(len(ccts), 0)

if __name__ == "__main__":
    unittest.main()
