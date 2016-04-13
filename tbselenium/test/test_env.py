from tbselenium.utils import is_port_listening, run_cmd
import unittest
from tbselenium import common as cm


class EnvironmentTest(unittest.TestCase):
    def assert_py_pkg_installed(self, pkg_name):
        try:
            __import__(pkg_name)
        except ImportError:
            self.fail("Missing python package. Install it by running"
                      " '(sudo) pip install %s'" % pkg_name)

    def assert_installed(self, pkg_name):
        cmd = 'which %s' % pkg_name
        status, _ = self.run_cmd(cmd)
        self.assertFalse(status,
                         "%s is not installed. \
                         Install it by running '(sudo) apt-get install %s'" %
                         (pkg_name, pkg_name))

    @unittest.skip("We no longer depend on system tor")
    def test_tor_daemon_running(self):
        """Make sure we've a running tor process.
        The library can be used without having tor installed on the system,
        using Stem as a replacement.
        """

        cmd = "ps -ax | grep -w tor | grep -v grep"
        _, output = run_cmd(cmd)
        self.assertIn("/usr/bin/tor", output,
                      """Can't find the running tor process.
                      The tests (test_tbdriver) that depend on tor may fail.
                      You can run '(sudo) service tor start' to start tor.

                      If you don't want to run the tests, you may use Stem
                      instead of tor installed on the system.
                      """)

    @unittest.skip("We no longer depend on system tor")
    def test_default_tor_ports(self):
        """Make sure tor is listening on the port we expect."""
        self.assertTrue(is_port_listening(cm.DEFAULT_SOCKS_PORT),
                        """No process is listening on SOCKS port %s!""" %
                        cm.DEFAULT_SOCKS_PORT)

    def test_selenium(self):
        self.assert_py_pkg_installed('selenium')

    def test_py_selenium_version(self):
        import selenium
        pkg_ver = selenium.__version__
        err_msg = "Python Selenium package should be greater than 2.45.0"
        min_v = 2
        min_minor_v = 45
        min_micro_v = 0
        version, minor_v, micro_v = pkg_ver.split('.')
        self.assertGreaterEqual(version, min_v, err_msg)
        if version == min_v:
            self.assertGreaterEqual(minor_v, min_minor_v, err_msg)
            if minor_v == min_minor_v:
                self.assertGreaterEqual(micro_v, min_micro_v, err_msg)


if __name__ == "__main__":
    unittest.main()
