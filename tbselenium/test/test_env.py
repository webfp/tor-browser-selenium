import pytest
import unittest
from selenium.webdriver.common.utils import is_connectable
from tbselenium import common as cm


class EnvironmentTest(unittest.TestCase):
    def assert_py_pkg_installed(self, pkg_name):
        try:
            __import__(pkg_name)
        except ImportError:
            self.fail("Missing python package. Install it by running"
                      " '(sudo) pip install %s'" % pkg_name)

    @pytest.mark.skipif(not cm.TRAVIS, reason="Only runs on CI")
    def test_default_tor_ports(self):
        """Make sure tor is listening on the port we expect."""
        self.assertTrue(is_connectable(cm.DEFAULT_SOCKS_PORT))

    def test_selenium(self):
        self.assert_py_pkg_installed('selenium')

    def test_py_selenium_version(self):
        # TODO use LooseVersion
        import selenium
        pkg_ver = selenium.__version__
        err_msg = "Python Selenium package should be greater than 2.45.0"
        min_v = 2
        min_minor_v = 45
        min_micro_v = 0
        version, minor_v, micro_v = [int(v) for v in pkg_ver.split('.')]
        self.assertGreaterEqual(version, min_v, err_msg)
        if version == min_v:
            self.assertGreaterEqual(minor_v, min_minor_v, err_msg)
            if minor_v == min_minor_v:
                self.assertGreaterEqual(micro_v, min_micro_v, err_msg)


if __name__ == "__main__":
    unittest.main()
