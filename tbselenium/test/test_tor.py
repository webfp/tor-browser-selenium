import unittest
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.utils import is_busy
from tbselenium.test import TBB_PATH
import tbselenium.common as cm


class Test(unittest.TestCase):

    def test_running_with_system_tor(self):
        if not is_busy(cm.DEFAULT_SOCKS_PORT):
            self.fail("System Tor doesn't appear to be running.")

        with TBDriverFixture(TBB_PATH,
                             tor_cfg=cm.USE_RUNNING_TOR,
                             socks_port=cm.DEFAULT_SOCKS_PORT,
                             control_port=cm.DEFAULT_CONTROL_PORT) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")


if __name__ == "__main__":
    unittest.main()
