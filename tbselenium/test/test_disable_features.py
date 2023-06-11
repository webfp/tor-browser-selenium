import unittest
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import LOCAL_JS_TEST_URL, LOCAL_IMG_TEST_URL
from tbselenium.utils import disable_js, get_js_status_text


class DisableFeaturesTest(unittest.TestCase):

    def test_disable_js(self):
        with TBDriverFixture(TBB_PATH) as driver:
            disable_js(driver)
            driver.load_url_ensure(LOCAL_JS_TEST_URL)
            js_status = get_js_status_text(driver)
            assert js_status == "JavaScript is disabled."

    def test_disable_images(self):
        """Make sure we disable images via a pref."""

        PREF_DICT = {
            "permissions.default.image": 2,
            # 2 means block images from loading.
            # http://kb.mozillazine.org/Permissions.default.image#2
        }

        with TBDriverFixture(TBB_PATH, pref_dict=PREF_DICT) as driver:
            driver.load_url(LOCAL_IMG_TEST_URL)
            is_img_loaded = driver.execute_script(
                "return document.querySelector('img#onion').complete === true")
            assert not is_img_loaded, "Image should not be loaded"

    def test_enable_images(self):
        """Make sure images are enabled by default."""

        with TBDriverFixture(TBB_PATH) as driver:
            driver.load_url(LOCAL_IMG_TEST_URL)
            is_img_loaded = driver.execute_script(
                "return document.querySelector('img#onion').complete === true")
            assert is_img_loaded, "Image should be loaded"


if __name__ == "__main__":
    unittest.main()
