import unittest
import pytest
import tempfile
from os import environ
from os.path import join, dirname

from tbselenium.test.fixtures import launch_tor_with_config_fixture
from tbselenium.test.fixtures import TorBrowserDriverFixture as TBDriverFixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH


class TBStemTest(unittest.TestCase):

    def test_running_with_stem(self):
        """We should be able to run with a tor process started with Stem."""
        try:
            from stem.control import Controller
        except ImportError as err:
            pytest.skip("Can't import Stem. Skipping test: %s" % err)
        custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
        environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)
        # any port would do, pick 9250, 9251 to avoid conflict
        socks_port = 9250
        control_port = 9251
        temp_data_dir = tempfile.mkdtemp()
        torrc = {'ControlPort': str(control_port),
                 'SOCKSPort': str(socks_port),
                 'DataDirectory': temp_data_dir}
        tor_process = launch_tor_with_config_fixture(config=torrc,
                                                     tor_cmd=custom_tor_binary)
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR,
                                 socks_port=socks_port) as driver:
                driver.load_url_ensure(cm.CHECK_TPO_URL)
                driver.find_element_by("h1.on")

        if tor_process:
            tor_process.kill()

if __name__ == "__main__":
    unittest.main()
