import unittest
import pytest
from selenium.webdriver.common.utils import is_connectable
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
import tbselenium.common as cm


class Test(unittest.TestCase):

    def test_running_with_system_tor(self):
        if not is_connectable(cm.DEFAULT_SOCKS_PORT):
            pytest.skip("Skipping. Start system Tor to run this test.")

        with TBDriverFixture(TBB_PATH, tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
            driver.find_element_by("h1.on")


if __name__ == "__main__":
    unittest.main()
