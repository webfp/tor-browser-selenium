import sys
import re
import tempfile
import pytest
import unittest
from os import environ, listdir
from os.path import join, basename
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
import tbselenium.utils as ut


@pytest.mark.skipif(sys.platform != 'linux2', reason='Requires Linux')
class TBBundledFonts(unittest.TestCase):
    """Use fontconfig's FC_DEBUG logs to test font bundling."""

    @classmethod
    def setUpClass(cls):
        _, log_file = tempfile.mkstemp()

        # https://www.freedesktop.org/software/fontconfig/fontconfig-user.html
        environ["FC_DEBUG"] = "%d" % (1024 + 8 + 1)
        cls.driver = TBDriverFixture(TBB_PATH, tbb_logfile_path=log_file)
        driver = cls.driver
        driver.load_url_ensure("https://www.wikipedia.org/")
        cls.log_txt = ut.read_file(log_file)
        cls.bundled_fonts_dir = join(driver.tbb_path,
                                     cm.DEFAULT_BUNDLED_FONTS_PATH)
        cls.bundled_font_files = set(listdir(cls.bundled_fonts_dir))

    @classmethod
    def tearDownClass(cls):
        environ["FC_DEBUG"] = "0"
        if cls.driver:
            cls.driver.quit()

    def test_should_load_font_config_file(self):
        fonts_conf_path = join(self.driver.tbb_path,
                               cm.DEFAULT_FONTS_CONF_PATH)
        expected_log = "Loading config file %s" % fonts_conf_path
        self.assertIn(expected_log, self.log_txt)

    def test_should_add_bundled_fonts(self):
        expected_pattern = r"adding fonts from\s?%s" % self.bundled_fonts_dir
        self.assertRegexpMatches(self.log_txt, expected_pattern)

    def test_should_not_fail_to_choose_fonts(self):
        ugly_warning = "failed to choose a font, expect ugly output"
        self.assertNotIn(ugly_warning, self.log_txt)

    def test_tbb_should_include_bundled_font_files(self):
        self.assertTrue(len(self.bundled_font_files) > 0)

    def test_should_only_load_and_use_bundled_fonts(self):
        used_font_files = set()
        # search in fontconfig logs
        for _, ttf, _ in re.findall(r"(file: \")(.*)(\".*)", self.log_txt):
            self.assertIn(self.bundled_fonts_dir, ttf)
            used_font_files.add(basename(ttf))
        self.assertEqual(used_font_files, self.bundled_font_files)


if __name__ == "__main__":
    unittest.main()
