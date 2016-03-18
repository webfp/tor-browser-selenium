import unittest
from os import environ
from os.path import join, dirname, expanduser
from time import sleep

import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.test import TBB_PATH


class TorBrowserDriverExamples(unittest.TestCase):
    """
    This class shows examples of how to use the TroBrowserDriver.
    """

    @unittest.skip("Only for didactic purposes.")
    def test_visit_a_page(self):
        """The most basic use of the TorBrowserDriver.

        It assumes Tor is already running and SOCKS listening to the
        default port.
        """
        with TorBrowserDriver(TBB_PATH, virt_display="") as driver:
            driver.get(cm.TEST_URL)
            sleep(1)  # stay one second in the page

    @unittest.skip("Only for didactic purposes.")
    def test_take_screenshot(self):
        """Take screenshot of the page."""
        # We need to add an exception for canvas access in the Tor Browser
        # permission database. We need to do this for each site that we
        # plan to visit.
        TorBrowserDriver.add_exception(cm.TEST_URL)
        with TorBrowserDriver(TBB_PATH, virt_display="") as driver:
            driver.get(cm.TEST_URL)
            driver.get_screenshot_as_file("screenshot.png")

    @unittest.skip("Only for didactic purposes.")
    def test_visit_page_with_virt_display_enabled(self):
        """Visit a page with a virtual buffer."""
        with TorBrowserDriver(TBB_PATH, virt_display="1280X800") as driver:
            driver.get(cm.TEST_URL)  # this won't pop up the browser window.
            sleep(1)

    @unittest.skip("Only for didactic purposes.")
    def test_dont_pollute_profile(self):
        """This will make a temporary copy of the Tor Browser profile."""
        with TorBrowserDriver(TBB_PATH, pollute=False) as driver:
            driver.get(cm.TEST_URL)
            sleep(1)
            # the temporary profile is wiped when driver quits

    @unittest.skip("Only for didactic purposes.")
    def test_use_old_tor_browser_bundles(self):
        """Instead of passing the path to the Tor Browser Bundle,
        you can pass your own tor binary and profile. This is helpful
        for using the driver with old Tor Browser Bundles, where the
        directory structure is different from the one that is currently
        used by Tor developers.
        """
        # example for TBB 3.5, which we assume has been extracted in the home directory
        tbb_3_5 = join(expanduser('~'), 'tor-browser_en-US')
        tb_binary = join(tbb_3_5, "Browser", "firefox")
        tb_profile = join(tbb_3_5, "Data", "Browser", "profile.default")
        with TorBrowserDriver(tbb_binary_path=tb_binary,
                              tbb_profile_path=tb_profile,
                              tbb_logfile_path="ff.log") as driver:
            # as shown in the line above, you can also indicate the
            # log file for the Tor Browser (firefox log).
            driver.get(cm.TEST_URL)
            sleep(1)

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
                 'DataDirectory': join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)}
        # you can add your own settings to this torrc,
        # including the path and the level for logging in tor.
        # you can also use the DataDirectory property in torrc
        # to set a custom data directory for tor.
        # For other options see: https://www.torproject.org/docs/tor-manual.html.en
        tor_process = launch_tor_with_config(config=torrc, tor_cmd=custom_tor_binary)

        with Controller.from_port(port=custom_control_port) as controller:
            controller.authenticate()
            # Visit the page with the TorBrowserDriver
            with TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port) as driver:
                driver.get(cm.TEST_URL)
                sleep(1)

        # Kill tor process
        if tor_process:
            tor_process.kill()


if __name__ == "__main__":
    unittest.main()
