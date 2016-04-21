import unittest
from distutils.version import LooseVersion


class EnvironmentTest(unittest.TestCase):

    def test_selenium_version(self):
        import selenium
        pkg_ver = selenium.__version__
        self.assertGreaterEqual(LooseVersion(pkg_ver), LooseVersion("2.45"))


if __name__ == "__main__":
    unittest.main()
