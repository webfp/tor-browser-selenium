import unittest
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL, CI_ALPHA_TEST
from tbselenium.utils import set_security_level
from tbselenium.utils import SECURITY_HIGH, SECURITY_MEDIUM, SECURITY_LOW


GET_WEBGL_ORG_URL = "https://get.webgl.org/"


class SecurityLevelTest(unittest.TestCase):

    def get_webgl_test_page_status_text(self, driver):
        status = driver.find_element_by(
                    "h1.good", find_by=By.CSS_SELECTOR, timeout=5)
        return status.text

    def get_webgl_test_page_webgl_container_inner_html(self, driver):
        webgl_container = driver.find_element_by(
                    "logo-container", find_by=By.ID, timeout=5)
        return webgl_container.get_attribute('innerHTML').strip()

    def test_set_security_low(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is disabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Standard")
            except (NoSuchElementException, TimeoutException):
                pass

    def test_set_security_low_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_LOW)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = self.get_webgl_test_page_status_text(driver)
                assert status_text == "Your browser supports WebGL"

                # make sure WebGL is enabled
                webgl_container_inner_html = \
                    self.get_webgl_test_page_webgl_container_inner_html(driver)
                assert webgl_container_inner_html.startswith(
                    '<canvas id="webgl-logo"')

            except (NoSuchElementException, TimeoutException) as exc:
                self.fail(
                    "Security level does not seem to be set to Standard: %s"
                    % exc)

    def test_set_security_medium(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is disabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Standard")
            except (NoSuchElementException, TimeoutException):
                pass

    def test_set_security_medium_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_MEDIUM)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)
            try:
                # test the status text
                status_text = self.get_webgl_test_page_status_text(driver)
                assert status_text == "Your browser supports WebGL"

                # make sure WebGL is click-to-play (NoScript)
                webgl_container_inner_html = \
                    self.get_webgl_test_page_webgl_container_inner_html(driver)
                assert webgl_container_inner_html.startswith(
                    '<a class="__NoScript_PlaceHolder__')

            except (NoSuchElementException, TimeoutException) as exc:
                self.fail(
                    "Security level does not seem to be set to Medium: %s"
                    % exc)

    @pytest.mark.skipif(
        CI_ALPHA_TEST,
        reason="Not compatible with the current alpha (10.5a1)")
    def test_set_security_high(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            driver.load_url_ensure(CHECK_TPO_URL)
            try:
                driver.find_element_by("JavaScript is enabled.",
                                       find_by=By.LINK_TEXT, timeout=5)
                self.fail("Security level does not seem to be set to Safest")
            except (NoSuchElementException, TimeoutException):
                pass

    @pytest.mark.skipif(
        CI_ALPHA_TEST,
        reason="Not compatible with the current alpha (10.5a1)")
    def test_set_security_high_webgl(self):
        with TBDriverFixture(TBB_PATH) as driver:
            set_security_level(driver, SECURITY_HIGH)
            driver.load_url_ensure(GET_WEBGL_ORG_URL)

            try:
                status_text = self.get_webgl_test_page_status_text(driver)
                assert status_text == ""
            except (NoSuchElementException, TimeoutException):
                self.fail("Security level does not seem to be set to Safest")


if __name__ == "__main__":
    unittest.main()
