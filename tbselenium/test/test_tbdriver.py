import tempfile
import unittest
import pytest
from os import environ
from os.path import join, isdir, getmtime
from time import time

from selenium.webdriver.common.timeouts import Timeouts
from selenium.common.exceptions import TimeoutException
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture


class TBDriverTest(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDriverFixture(TBB_PATH)

    def tearDown(self):
        self.tb_driver.quit()

    def test_should_load_check_tpo(self):
        congrats = "Congratulations. This browser is configured to use Tor."
        self.tb_driver.load_url_ensure(cm.CHECK_TPO_URL)
        status = self.tb_driver.find_element_by("h1.on")
        self.assertEqual(status.text, congrats)

    def test_should_load_hidden_service(self):
        TPO_ONION_URL = "http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion/index.html"  # noqa
        self.tb_driver.load_url_ensure(TPO_ONION_URL, wait_for_page_body=True)
        self.assertEqual(
            'Tor Project | Anonymity Online',
            self.tb_driver.title)

    def test_should_check_environ_in_prepend(self):
        self.tb_driver.quit()
        self.tb_driver = TBDriverFixture(TBB_PATH)
        paths = environ["PATH"].split(':')
        tbbpath_count = paths.count(self.tb_driver.tbb_browser_dir)
        self.assertEqual(tbbpath_count, 1)

    def test_should_set_timeouts(self):
        LOW_PAGE_LOAD_LIMIT = 0.05
        self.tb_driver.timeouts = Timeouts(page_load=LOW_PAGE_LOAD_LIMIT)
        timed_out = False
        t_before_load = time()
        try:
            self.tb_driver.load_url(cm.CHECK_TPO_URL)
        except TimeoutException:
            timed_out = True
        finally:
            t_spent = time() - t_before_load
            self.assertAlmostEqual(t_spent, LOW_PAGE_LOAD_LIMIT, delta=1)
            assert timed_out


class TBDriverCleanUp(unittest.TestCase):
    def setUp(self):
        self.tb_driver = TBDriverFixture(TBB_PATH)

    def test_should_terminate_geckodriver_process_on_quit(self):
        driver = self.tb_driver
        geckodriver_process = driver.service.process
        self.assertEqual(geckodriver_process.poll(), None)
        driver.quit()
        self.assertNotEqual(geckodriver_process.poll(), None)

    def test_should_remove_profile_dirs_on_quit(self):
        temp_profile_dir = self.tb_driver.temp_profile_dir
        self.assertTrue(isdir(temp_profile_dir))
        self.tb_driver.quit()
        self.assertFalse(isdir(temp_profile_dir))


class TBDriverTorDataDir(unittest.TestCase):

    TOR_DATA_PATH = join(TBB_PATH, cm.DEFAULT_TOR_DATA_PATH)

    @pytest.mark.skipif(cm.TRAVIS, reason="Requires Tor bootstrap,"
                        "unreliable on Travis")
    def test_temp_tor_data_dir(self):
        """Tor data directory in TBB should not be modified if
        we use a separate tor_data_dir.
        """
        tmp_dir = tempfile.mkdtemp()
        mod_time_before = getmtime(self.TOR_DATA_PATH)
        with TBDriverFixture(TBB_PATH, tor_data_dir=tmp_dir) as driver:
            driver.load_url_ensure(cm.CHECK_TPO_URL)
        mod_time_after = getmtime(self.TOR_DATA_PATH)
        self.assertEqual(mod_time_before, mod_time_after)


if __name__ == "__main__":
    unittest.main()
