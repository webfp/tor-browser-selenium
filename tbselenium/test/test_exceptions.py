import unittest
import tempfile

from selenium.webdriver.common.utils import free_port

from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium import common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.exceptions import (TBDriverPathError,
                                   TBDriverPortError,
                                   TBDriverConfigError)

MISSING_DIR = "_no_such_directory_"
MISSING_FILE = "_no_such_file_"


class TBDriverExceptions(unittest.TestCase):

    def test_should_raise_for_missing_paths(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver()
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Either TBB path or Firefox profile and binary path "
                         "should be provided ")

    def test_should_raise_for_missing_tbb_path(self):
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "TBB path is not a directory %s" % MISSING_DIR)

    def test_should_raise_for_missing_fx_binary(self):
        temp_dir = tempfile.mkdtemp()
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=MISSING_FILE,
                             tbb_profile_path=temp_dir)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox binary %s" % MISSING_FILE)

    def test_should_raise_for_missing_fx_profile(self):
        _, temp_file = tempfile.mkstemp()
        with self.assertRaises(TBDriverPathError) as exc:
            TorBrowserDriver(tbb_fx_binary_path=temp_file,
                             tbb_profile_path=MISSING_DIR)
        exc_msg = exc.exception
        self.assertEqual(str(exc_msg),
                         "Invalid Firefox profile dir %s" % MISSING_DIR)

    def test_should_raise_for_invalid_pref_dict(self):
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict="foo")
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=[1, 2])
        with self.assertRaises(AttributeError):
            TorBrowserDriver(TBB_PATH, pref_dict=(1, 2))

    def test_should_fail_launching_tor_on_custom_socks_port(self):
        with self.assertRaises(TBDriverPortError):
            TorBrowserDriver(TBB_PATH, socks_port=free_port(),
                             tor_cfg=cm.LAUNCH_NEW_TBB_TOR)

    def test_should_not_load_with_wrong_sys_socks_port(self):
        with self.assertRaises(TBDriverPortError):
            TorBrowserDriver(TBB_PATH, socks_port=free_port(),
                             tor_cfg=cm.USE_RUNNING_TOR)

    def test_should_raise_for_invalid_tor_config(self):
        with self.assertRaises(TBDriverConfigError):
            TorBrowserDriver(TBB_PATH, tor_cfg=-1)

    def test_fixture_should_raise_for_invalid_tor_config(self):
        with self.assertRaises(TBDriverConfigError):
            TBDriverFixture(TBB_PATH, tor_cfg=-1)

if __name__ == "__main__":
    unittest.main()
