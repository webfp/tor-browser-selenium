import unittest
from subprocess import check_output
from packaging.version import Version

# https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
MINIMUM_SELENIUM_VERSION = "3.14"


class EnvironmentTest(unittest.TestCase):

    def test_selenium_version(self):
        import selenium
        pkg_ver = selenium.__version__
        self.assertGreaterEqual(Version(pkg_ver), Version(MINIMUM_SELENIUM_VERSION))

    def test_geckodriver_version(self):
        """Make sure that the recommended geckodriver version is installed."""
        GECKODRIVER_VERSION_STR = "geckodriver 0.35.0"  # TODO: DRY
        gd_v_out = check_output(["geckodriver", "-V"]).decode("utf-8")
        self.assertIn(GECKODRIVER_VERSION_STR, gd_v_out.split("\n")[0])


if __name__ == "__main__":
    unittest.main()
