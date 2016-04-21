import unittest
import pytest
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.utils import is_busy
from tbselenium.test import TBB_PATH
import tbselenium.common as cm


class Test(unittest.TestCase):

    def test_running_with_system_tor(self):
        if not is_busy(cm.DEFAULT_SOCKS_PORT):
            if cm.TRAVIS:  # Tor should be running on CI
                self.fail("Skipping. Start system Tor to run this test.")
            else:
                pytest.skip("Skipping. Start the system Tor to run this test.")

        with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")


if __name__ == "__main__":
    unittest.main()
