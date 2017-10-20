import unittest
# from time import sleep

from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture

CONGRATS = "Congratulations. This browser is configured to use Tor."


class TBDriverBridgeTest(unittest.TestCase):
    def tearDown(self):
        self.tb_driver.quit()

    def should_load_check_tpo_via_bridge(self, bridge_type):
        self.tb_driver = TBDriverFixture(TBB_PATH,
                                         default_bridge_type=bridge_type)
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        status = self.tb_driver.find_element_by("h1.on")
        self.assertEqual(status.text, CONGRATS)
        # sleep(0)  # the bridge type in use is manually verified by
        # checking the Tor Network Settings dialog.
        # We set a sleep of a few seconds and exported NO_XVFB=1 to do that
        # manually.

        # TODO: find a way to automatically verify the bridge in use
        # This may be possible with geckodriver, since it can interact
        # with chrome as well.

    def test_should_load_check_tpo_via_meek_amazon_bridge(self):
        self.should_load_check_tpo_via_bridge("meek-amazon")

    def test_should_load_check_tpo_via_meek_azure_bridge(self):
        self.should_load_check_tpo_via_bridge("meek-azure")

    def test_should_load_check_tpo_via_meek_obfs3_bridge(self):
        self.should_load_check_tpo_via_bridge("obfs3")

    def test_should_load_check_tpo_via_obfs4_bridge(self):
        self.should_load_check_tpo_via_bridge("obfs4")

    def test_should_load_check_tpo_via_fte_bridge(self):
        self.should_load_check_tpo_via_bridge("fte")
