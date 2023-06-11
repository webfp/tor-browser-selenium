import unittest
from os.path import dirname, abspath, join
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import LOCAL_JS_TEST_URL
from tbselenium.utils import set_security_level, get_js_status_text
from tbselenium.utils import (
    TB_SECURITY_LEVEL_SAFEST,
    TB_SECURITY_LEVEL_SAFER,
    TB_SECURITY_LEVEL_STANDARD
    )


GET_WEBGL_ORG_URL = "https://get.webgl.org/"


class SecurityLevelTest(unittest.TestCase):

    def get_webgl_test_page_webgl_container_inner_html(self, driver):
        webgl_container = driver.find_element(By.ID, "logo-container")
        return webgl_container.get_attribute('innerHTML').strip()

    def test_set_security_standard(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_STANDARD)
            driver.load_url_ensure(LOCAL_JS_TEST_URL)
            js_status = get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_standard_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_STANDARD)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = driver.find_element(By.ID, "support").text
                assert status_text.startswith("Your browser supports WebGL")

                # make sure WebGL is enabled
                webgl_container_inner_html = \
                    self.get_webgl_test_page_webgl_container_inner_html(driver)
                assert webgl_container_inner_html.startswith(
                    '<canvas id="webgl-logo"')

            except (NoSuchElementException, TimeoutException) as exc:
                self.fail(
                    "Security level cannot be set to 'Standard': %s"
                    % exc)

    def test_set_security_safer(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_SAFER)
            driver.load_url_ensure(LOCAL_JS_TEST_URL)
            js_status = get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_safer_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_SAFER)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = driver.find_element(By.ID, "support").text
                assert status_text.startswith(
                    "Hmm. While your browser seems to support WebGL, it is "
                    "disabled or unavailable. If possible, please ensure that "
                    "you are running the latest drivers for your video card.")

                # make sure WebGL is click-to-play (NoScript)
                webgl_container_inner_html = \
                    self.get_webgl_test_page_webgl_container_inner_html(driver)
                assert webgl_container_inner_html.startswith(
                    '<a class="__NoScript_PlaceHolder__')

            except (NoSuchElementException, TimeoutException) as exc:
                self.fail(
                    "Security level cannot to be set to 'Safer': %s"
                    % exc)

    def test_set_security_safest(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_SAFEST)
            driver.load_url_ensure(LOCAL_JS_TEST_URL)
            js_status = get_js_status_text(driver)
            assert js_status == "JavaScript is disabled."

    def test_set_security_safest_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, TB_SECURITY_LEVEL_SAFEST)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                status = driver.find_element(By.ID, "support").text
                assert status == "You must enable JavaScript to use WebGL."
            except (NoSuchElementException, TimeoutException):
                self.fail("Security level cannot be set to 'Safest'")


if __name__ == "__main__":
    unittest.main()
