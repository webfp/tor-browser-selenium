import unittest
from os import environ
from os.path import join, dirname, expanduser
from time import sleep

import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH


class TorBrowserDriverExamples(unittest.TestCase):
    """
    This class shows examples of how to use the TorBrowserDriver.
    """

    @unittest.skip("Only for didactic purposes.")
    def test_visit_a_page(self):
        """The most basic use of the TorBrowserDriver."""
        with TorBrowserDriver(TBB_PATH) as driver:
            driver.get(cm.TEST_URL)
            sleep(1)  # stay one second on the page

    @unittest.skip("Only for didactic purposes.")
    def test_use_old_tor_browser_bundles(self):
        """Instead of passing the path to the Tor Browser Bundle,
        you can pass your own tor binary and profile. This is helpful
        for using the driver with old Tor Browser Bundles, where the
        directory structure is different from the one that is currently
        used by Tor developers.
        """
        # Assume we've extracted TBB 3.5 to our home directory
        tbb_3_5 = join(expanduser('~'), 'tor-browser_en-US')
        tb_binary = join(tbb_3_5, "Browser", "firefox")
        tb_profile = join(tbb_3_5, "Data", "Browser", "profile.default")
        with TorBrowserDriver(tbb_binary_path=tb_binary,
                              tbb_profile_path=tb_profile,
                              tbb_logfile_path="ff.log") as driver:
            driver.get(cm.TEST_URL)

    @unittest.skip("Only for didactic purposes.")
    def test_run_driver_with_stem_customized(self):
        """This test shows how to run the TorBrowserDriver with stem.

        It shows how to launch tor with stem listening to a custom SOCKS
        and Controller ports, and use a particular tor binary instead of
        the one installed in the system.
        """
        from stem.control import Controller
        from stem.process import launch_tor_with_config

        # If you're running tor with the TBB binary, instead
        # of a tor installed in the system, you need to set
        # its path in the LD_LIBRARY_PATH:
        custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
        environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)

        # Run tor
        custom_control_port, custom_socks_port = 9051, 9050
        torrc = {'ControlPort': str(custom_control_port),
                 'SOCKSPort': str(custom_socks_port),
                 'DataDirectory': join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)}
        # you can add your own settings to this torrc,
        # including the path and the level for logging in tor.
        # you can also use the DataDirectory property in torrc
        # to set a custom data directory for tor.
        # See other options: https://www.torproject.org/docs/tor-manual.html.en
        tor_process = launch_tor_with_config(config=torrc,
                                             tor_cmd=custom_tor_binary)

        with Controller.from_port(port=custom_control_port) as controller:
            controller.authenticate()
            # Visit the page with the TorBrowserDriver
            with TorBrowserDriver(TBB_PATH,
                                  socks_port=custom_socks_port) as driver:
                driver.get(cm.TEST_URL)
                sleep(1)

        # Kill tor process
        if tor_process:
            tor_process.kill()


if __name__ == "__main__":
    unittest.main()
