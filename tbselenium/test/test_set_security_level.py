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
WAIT_AFTER_PAGE_LOAD = 3  # in seconds


class SecurityLevelTest(unittest.TestCase):

    def get_webgl_test_page_webgl_container_inner_html(self, driver):
        webgl_container = driver.find_element(By.ID, "logo-container")
        return webgl_container.get_attribute('innerHTML').strip()

    def get_js_status_text(self, driver):
        return driver.find_element(By.ID, 'js').\
                get_attribute("innerText")

    def test_set_security_low(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                CHECK_TPO_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_low_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                GET_WEBGL_ORG_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
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

    def test_set_security_medium(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                CHECK_TPO_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is enabled."

    def test_set_security_medium_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                GET_WEBGL_ORG_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
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

    def test_set_security_high(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            # We need either "new tab" or refresh the page
            # (via driver.refresh()) after page load for this setting the
            # take effect. If we don't open a new tab the test becomes flaky
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                CHECK_TPO_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
            driver.refresh()
            js_status = self.get_js_status_text(driver)
            assert js_status == "JavaScript is disabled."

    def test_set_security_high_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            # We need either "new tab" or refresh the page
            # (via driver.refresh()) after page load for this setting the
            # take effect. If we don't open a new tab the test becomes flaky
            driver.switch_to.new_window('tab')
            driver.load_url_ensure(
                GET_WEBGL_ORG_URL, wait_on_page=WAIT_AFTER_PAGE_LOAD)
            try:
                status = driver.find_element(By.ID, "support").text
                assert status == "You must enable JavaScript to use WebGL."
            except (NoSuchElementException, TimeoutException):
                self.fail("Security level cannot be set to 'Safest'")


if __name__ == "__main__":
    unittest.main()
