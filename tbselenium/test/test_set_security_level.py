import unittest
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL
from tbselenium.utils import set_security_level
from tbselenium.utils import SECURITY_HIGH, SECURITY_MEDIUM, SECURITY_LOW


GET_WEBGL_ORG_URL = "https://get.webgl.org/"


class SecurityLevelTest(unittest.TestCase):

    def get_webgl_test_page_webgl_container_inner_html(self, driver):
        webgl_container = driver.find_element_by_id("logo-container")
        return webgl_container.get_attribute('innerHTML').strip()

    def get_js_status_text(self, driver):
        return driver.find_element_by_id('js').\
                get_attribute("innerText")

    def test_set_security_low(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.load_url_ensure(CHECK_TPO_URL)
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_low_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = driver.find_element_by_id("support").text
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

    def test_set_security_medium(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.load_url_ensure(CHECK_TPO_URL)
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_medium_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = driver.find_element_by_id("support").text
                assert status_text.startswith("Your browser supports WebGL")
                experimental = driver.find_element_by_id("webgl-experimental")
                assert "However, it indicates that support is experimental; "
                "Not all WebGL functionality may be supported, and content may"
                " not run as expected." == experimental.text

                # make sure WebGL is click-to-play (NoScript)
                webgl_container_inner_html = \
                    self.get_webgl_test_page_webgl_container_inner_html(driver)
                assert webgl_container_inner_html.startswith(
                    '<a class="__NoScript_PlaceHolder__')

            except (NoSuchElementException, TimeoutException) as exc:
                self.fail(
                    "Security level cannot to be set to 'Safer': %s"
                    % exc)

    def test_set_security_high(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            driver.load_url_ensure(CHECK_TPO_URL)
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is disabled."

    def test_set_security_high_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)

            try:
                status = driver.find_element_by_id("support").text
                assert status == "You must enable JavaScript to use WebGL."
            except (NoSuchElementException, TimeoutException):
                self.fail("Security level cannot be set to 'Safest'")


if __name__ == "__main__":
    unittest.main()
