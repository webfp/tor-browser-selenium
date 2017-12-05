import unittest
from subprocess import check_output
from distutils.version import LooseVersion


class EnvironmentTest(unittest.TestCase):

    def test_selenium_version(self):
        import selenium
        pkg_ver = selenium.__version__
        self.assertGreaterEqual(LooseVersion(pkg_ver), LooseVersion("2.45"))

    def test_geckodriver_version(self):
        """Make sure that the right geckodriver version is installed."""
        GECKODRIVER_VERSION_STR = "geckodriver 0.17.0"
        gd_v_out = check_output(["geckodriver", "-V"]).decode("utf-8")
        self.assertEqual(GECKODRIVER_VERSION_STR, gd_v_out.split("\n")[0])


if __name__ == "__main__":
    unittest.main()
