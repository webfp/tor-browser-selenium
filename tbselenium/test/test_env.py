import unittest
from subprocess import check_output
from distutils.version import LooseVersion


# https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
MINIMUM_SELENIUM_VERSION = "3.14"


class EnvironmentTest(unittest.TestCase):

    def test_selenium_version(self):
        import selenium
        pkg_ver = selenium.__version__
        self.assertGreaterEqual(LooseVersion(pkg_ver), LooseVersion(MINIMUM_SELENIUM_VERSION))

    def test_geckodriver_version(self):
        """Make sure that the right geckodriver version is installed."""
        GECKODRIVER_VERSION_STR = "geckodriver 0.27.0"
        gd_v_out = check_output(["geckodriver", "-V"]).decode("utf-8")
        self.assertIn(GECKODRIVER_VERSION_STR, gd_v_out.split("\n")[0])


if __name__ == "__main__":
    unittest.main()
