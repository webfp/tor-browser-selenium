import time
import unittest

import tbbselenium.common as cm
from tbbselenium.tbdriver import TorBrowserDriver
from tbbselenium.tor_controller import TorController

# Test URLs are taken from the TBB test suit
# https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/tree/mozmill-tests/tbb-tests/https-everywhere.js
HTTP_URL = "http://www.mediawiki.org/wiki/MediaWiki"
HTTPS_URL = "https://www.mediawiki.org/wiki/MediaWiki"


class TestTorUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tor_controller = TorController(cm.TORRC_WANG_AND_GOLDBERG,
                                           cm.TBB_DEFAULT_VERSION)
        cls.tor_process = cls.tor_controller.launch_tor_service()

    def test_launch_tor_service(self):
        self.tor_process.kill()
        self.tor_process = self.tor_controller.launch_tor_service()
        self.assertTrue(self.tor_process, 'Cannot launch Tor process')

    def test_close_all_streams(self):
        streams_open = False
        new_tb_drv = TorBrowserDriver()
        new_tb_drv.get('http://www.google.com')
        time.sleep(cm.WAIT_IN_SITE)
        self.tor_controller.close_all_streams()
        for stream in self.tor_controller.controller.get_streams():
            print stream.id, stream.purpose, stream.target_address, "open!"
            streams_open = True
        new_tb_drv.quit()
        self.assertFalse(streams_open, 'Could not close all streams.')

    @classmethod
    def tearDownClass(cls):
        # cls.tor_process.kill()
        cls.tor_controller.kill_tor_proc()

if __name__ == "__main__":
    unittest.main()
