import os
import sys
import unittest
import commands
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import common as cm


class Test(unittest.TestCase):
    def assert_py_pkg_installed(self, pkg_name):
        try:
            __import__(pkg_name)
        except:
            self.fail('Cannot find python package.\
                        Install it by sudo pip install %s' % pkg_name)

    def run_cmd(self, cmd):
        return commands.getstatusoutput('%s ' % cmd)

    def assert_installed(self, pkg_name, msg=""):
        cmd = 'which %s' % pkg_name
        status, _ = self.run_cmd(cmd)
        self.assertFalse(status, "%s is not installed."
                         "Install it with sudo apt-get install %s" %
                         (pkg_name, pkg_name))

    def test_dumpcap(self):
        self.assert_installed('dumpcap')

    def test_xvfb(self):
        self.assert_installed('Xvfb')

    def test_stem(self):
        self.assert_py_pkg_installed('stem')

    def test_psutil(self):
        self.assert_py_pkg_installed('psutil')

    def test_xvfbwrapper(self):
        self.assert_py_pkg_installed('xvfbwrapper')

    def test_argparse(self):
        self.assert_py_pkg_installed('argparse')

    def test_requests(self):
        self.assert_py_pkg_installed('requests')

    def test_webfp_path(self):
        self.assertTrue(os.path.isdir(cm.BASE_DIR),
                        'Cannot find base dir path %s' % cm.BASE_DIR)

    def test_tb_bin_path(self):
        tb_bin_path = cm.get_tb_bin_path(version=cm.TBB_DEFAULT_VERSION)
        self.assertTrue(os.path.isfile(tb_bin_path),
                        'Cannot find Tor Browser binary path %s'
                        % tb_bin_path)

    def test_tbb_profile_path(self):
        tbb_profile_path = cm.get_tbb_profile_path(cm.TBB_DEFAULT_VERSION)
        self.assertTrue(os.path.isdir(tbb_profile_path),
                        'Cannot find Tor Browser profile dir %s'
                        % tbb_profile_path)

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
