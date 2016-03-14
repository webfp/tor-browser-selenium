import time
import unittest

from os import environ
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.torcontroller import TorController

import tbselenium.common as cm

# Environment variable that points to TBB directory:
TBB_PATH = environ.get('TBB_PATH')
if TBB_PATH is None:
    raise RuntimeError("Environment variable `TBB_PATH` with TBB directory not found.")


class RunDriverWithControllerTest(unittest.TestCase):
    """
    This test shows how to run tor with TorController and browse with TorBrowserDriver.
    """
    @unittest.skip("Only for didactic purposes.")
    def test_run_driver_with_controller(self):
        # run controller on port N
        custom_socks_port = 6666
        self.tor_controller = TorController(TBB_PATH, torrc_dict={'SocksPort': str(custom_socks_port)})
        self.tor_process = self.tor_controller.launch_tor_service()

        # set driver and get a page
        self.tor_driver = TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port)
        self.tor_driver.get(cm.TEST_URL)

        # shutdown
        self.tor_driver.quit()
        self.tor_controller.kill_tor_proc()


class TorControllerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tor_controller = TorController(TBB_PATH)
        cls.tor_process = cls.tor_controller.launch_tor_service()

    def test_close_all_streams(self):
        streams_open = False
        new_tb_drv = TorBrowserDriver(TBB_PATH)
        new_tb_drv.get('http://www.google.com')
        time.sleep(30)
        self.tor_controller.close_all_streams()
        for stream in self.tor_controller.controller.get_streams():
            print stream.id, stream.purpose, stream.target_address, "open!"
            streams_open = True
        new_tb_drv.quit()
        self.assertFalse(streams_open, 'Could not close all streams.')

    @classmethod
    def tearDownClass(cls):
        cls.tor_controller.kill_tor_proc()

if __name__ == "__main__":
    unittest.main()
