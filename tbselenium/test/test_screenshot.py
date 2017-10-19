import unittest
import tempfile
from os import remove
from os.path import getsize, exists

from tbselenium.test.fixtures import TBDriverFixture
from tbselenium import common as cm
from tbselenium.test import TBB_PATH

# A blank image for https://check.torproject.org/ amounts to ~4.8KB.
# A real screen capture of the same page is ~57KB. If the capture
# is not blank it should be at least greater than 20KB.
SCREENSHOT_MIN_SIZE = 2000


class ScreenshotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _, cls.temp_file = tempfile.mkstemp(suffix=".png")
        cls.driver = TBDriverFixture(TBB_PATH)
        cls.driver.load_url_ensure(cm.CHECK_TPO_URL, 3)

    @classmethod
    def tearDownClass(cls):
        if exists(cls.temp_file):
            remove(cls.temp_file)
        cls.driver.quit()

    def test_screenshot_as_file(self):
        self.driver.get_screenshot_as_file(self.temp_file)
        self.assertGreater(getsize(self.temp_file), SCREENSHOT_MIN_SIZE)

    def test_screenshot_as_base64(self):
        base64_img = self.driver.get_screenshot_as_base64()
        self.assertGreater(len(base64_img), SCREENSHOT_MIN_SIZE)

    def test_screenshot_as_png(self):
        png_data = self.driver.get_screenshot_as_png()
        self.assertGreater(len(png_data), SCREENSHOT_MIN_SIZE)


if __name__ == "__main__":
    unittest.main()
