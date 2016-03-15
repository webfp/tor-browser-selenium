import unittest

import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH


class RunDriverWithStemTest(unittest.TestCase):
    """
    This test shows how to run the TorBrowserDriver with stem: https://stem.torproject.org
    """

    @unittest.skip("Only for didactic purposes.")
    def test_run_driver_with_controller(self):
        from stem.control import Controller
        with Controller.from_port() as controller:
        self.tor_driver = TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port)
        self.tor_driver.get(cm.TEST_URL)
        self.tor_driver.quit()


if __name__ == "__main__":
    unittest.main()
