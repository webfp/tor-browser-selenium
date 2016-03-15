import unittest

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
        tor_binary = "/etc/tor"
        logfile = "/tmp/tor.log"
        custom_control_port, custom_socks_port = 9050, 9051
        torrc = {'ControlPort': str(custom_control_port),
                 'Log': ['INFO file %s' % logfile]}
        tor_process = launch_tor_with_config(config=torrc,
                                             tor_cmd=tor_binary)

        # Get page with TorBrowserDriver
        with Controller.from_port(port=custom_control_port) as controller:
            controller.authenticate()
            tor_driver = TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port)
            tor_driver.get(cm.TEST_URL)
            tor_driver.quit()

        # Kill tor process
        if tor_process:
            tor_process.kill()


if __name__ == "__main__":
    unittest.main()
