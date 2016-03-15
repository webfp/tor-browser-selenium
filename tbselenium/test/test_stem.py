import unittest
from os.path import join

import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH


class RunDriverWithStemTest(unittest.TestCase):
    """
    This test shows how to run the TorBrowserDriver with stem: https://stem.torproject.org
    """
    @unittest.skip("Only for didactic purposes.")
    def test_run_driver_with_stem(self):
        from stem.control import Controller
        from stem.process import launch_tor_with_config

        # Run tor
        logfile = "/tmp/tor.log"
        custom_control_port, custom_socks_port = 9050, 9051
        tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
        torrc = {'ControlPort': str(custom_control_port),
                 'Log': ['INFO file %s' % logfile]}
        tor_process = launch_tor_with_config(config=torrc,
                                             tor_cmd=tor_binary)

        # Get page with TorBrowserDriver
        with Controller.from_port(port=custom_control_port) as controller:
            controller.authenticate()

            with TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port) as driver:
                driver.get(cm.TEST_URL)

        # Kill tor process
        if tor_process:
            tor_process.kill()


if __name__ == "__main__":
    unittest.main()
