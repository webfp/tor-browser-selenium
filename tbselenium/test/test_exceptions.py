import unittest
from os.path import isdir, join
import tempfile
import socket

from selenium.webdriver.common.utils import free_port

from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium import common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem, is_busy
from tbselenium.exceptions import (TBDriverPathError,
                                   TBDriverPortError,
                                   TBDriverConfigError, StemLaunchError)

MISSING_DIR = "_no_such_directory_"
MISSING_FILE = "_no_such_file_"


class TBDriverExceptions(unittest.TestCase):
    def setUp(self):
        self.open_sockets = []

    def tearDown(self):
        for skt in self.open_sockets:
            skt.close()

    def occupy_port(self, port_no):
        """Occupy the given port to simulate a port conflict."""
        if is_busy(port_no):  # already occupied, nothing to do
            return
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(("localhost", port_no))
        skt.listen(1)
        self.open_sockets.append(skt)

    def test_should_raise_for_missing_paths(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver()
        self.assertEqual(str(exc.exception),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided ")

    def test_should_raise_for_missing_tbb_path(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_path=MISSING_DIR)
        self.assertEqual(str(exc.exception),
                         "TBB path is not a directory %s" % MISSING_DIR)

    def test_should_raise_for_missing_fx_binary(self):
        tbb_profile_path = join(TBB_PATH, cm.DEFAULT_TBB_PROFILE_PATH)
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=MISSING_FILE,
                             tbb_profile_path=tbb_profile_path)
        self.assertEqual(str(exc.exception),
                         "Invalid Firefox binary %s" % MISSING_FILE)

    def test_should_raise_for_missing_fx_profile(self):
        fx_binary = join(TBB_PATH, cm.DEFAULT_TBB_FX_BINARY_PATH)
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=fx_binary,
                             tbb_profile_path=MISSING_DIR)
        self.assertEqual(str(exc.exception),
                         "Invalid Firefox profile dir %s" % MISSING_DIR)

    def test_should_raise_for_invalid_pref_dict(self):
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict="foo")
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=[1, 2])
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=(1, 2))

    def test_should_fail_launching_tbb_tor_on_custom_socks_port(self):
        with self.assertRaises(TBDriverPortError):
            TorBrowserDriver(TBB_PATH, socks_port=free_port(),
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR)

    def test_should_fail_launching_tbb_tor_on_used_socks_port(self):
        self.occupy_port(cm.DEFAULT_SOCKS_PORT)
        with self.assertRaises(TBDriverPortError) as exc:
            TorBrowserDriver(TBB_PATH,
                             socks_port=cm.DEFAULT_SOCKS_PORT,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR)
        self.assertEqual(str(exc.exception),
                         "SOCKS port %s is already in use"
                         % cm.DEFAULT_SOCKS_PORT)

    def test_should_fail_launching_tbb_tor_on_used_control_port(self):
        self.occupy_port(cm.DEFAULT_CONTROL_PORT)
        with self.assertRaises(TBDriverPortError) as exc:
            TorBrowserDriver(TBB_PATH,
                             control_port=cm.DEFAULT_CONTROL_PORT,
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR)
        self.assertEqual(str(exc.exception),
                         "Control port %s is already in use"
                         % cm.DEFAULT_CONTROL_PORT)

    def test_should_not_load_with_wrong_sys_socks_port(self):
        socks_port = free_port()
        with self.assertRaises(TBDriverPortError) as exc:
            TorBrowserDriver(TBB_PATH, socks_port=socks_port,
                             tor_cfg=cm.USE_RUNNING_TOR)

        self.assertEqual(str(exc.exception),
                         "SOCKS port %s is not listening" % socks_port)

    def test_should_raise_for_invalid_tor_config(self):
        with self.assertRaises(TBDriverConfigError):
            TorBrowserDriver(TBB_PATH, tor_cfg=-1)

    def test_fixture_should_raise_for_invalid_tor_config(self):
        with self.assertRaises(TBDriverConfigError):
            TBDriverFixture(TBB_PATH, tor_cfg=-1)

    def test_should_raise_for_stem(self):
        temp_dir = tempfile.mkdtemp()
        with self.assertRaises(StemLaunchError):
            launch_tbb_tor_with_stem()
        with self.assertRaises(StemLaunchError):
            launch_tbb_tor_with_stem(tbb_path="", tor_binary="")
        with self.assertRaises(StemLaunchError):
            launch_tbb_tor_with_stem(tbb_path=temp_dir, tor_binary="")

    def test_missing_browser(self):
        driver = TBDriverFixture(TBB_PATH)

        tempfolder = driver.profile.tempfolder
        profile_path = driver.profile.path

        self.assertTrue(isdir(tempfolder))
        self.assertTrue(isdir(profile_path))
        # kill the browser process
        if driver.w3c:
            driver.service.stop()
            driver.quit()
        else:
            driver.binary.kill()
            driver.quit()
        self.assertFalse(isdir(profile_path))
        self.assertFalse(isdir(tempfolder))


if __name__ == "__main__":
    unittest.main()
