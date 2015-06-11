import os
import sys
import unittest
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import common as cm
import utils as ut
import datacollection.visit as vi
from datacollection.torutils import TorController
join = os.path.join
TEST_URL = "https://torproject.org"


class VisitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tor_controller = TorController(cm.TORRC_WANG_AND_GOLDBERG,
                                           cm.TBB_DEFAULT_VERSION)
        cls.tor_process = cls.tor_controller.launch_tor_service()

    def check_expected_visit_dirs_and_files(self, visit):
        instance_ff_log_dir = join(inst_dir, "logs")
        self.assertTrue(os.path.isdir(instance_ff_log_dir))
        instance_ff_log = join(instance_ff_log_dir, "firefox.log")
        self.assertTrue(os.path.isfile(instance_ff_log))
        self.assertGreater(os.path.getsize(instance_ff_log), 0)

    def test_visit_with_defaults(self):
        self.setup_crawl_dirs()
        visit = vi.Visit(self.batch_num, self.site_num,
                         self.instance_num, TEST_URL,
                         self.site_dir, cm.TBB_DEFAULT_VERSION,
                         self.tor_controller)
        self.run_visit(visit)

    def test_visit_noxvfb(self):
        self.setup_crawl_dirs()
        visit = vi.Visit(self.batch_num, self.site_num,
                         self.instance_num, TEST_URL,
                         self.site_dir, cm.TBB_DEFAULT_VERSION,
                         self.tor_controller, bg_site=None,
                         experiment=cm.EXP_TYPE_WANG_AND_GOLDBERG, xvfb=False,
                         capture_screen=True)
        self.run_visit(visit)

    def test_screen_capture(self):
        cap_test_url = "https://check.torproject.org/"
        self.setup_crawl_dirs(cap_test_url)
        visit = vi.Visit(self.batch_num, self.site_num,
                         self.instance_num, cap_test_url,
                         self.site_dir, cm.TBB_DEFAULT_VERSION,
                         self.tor_controller, bg_site=None,
                         experiment=cm.EXP_TYPE_WANG_AND_GOLDBERG, xvfb=False,
                         capture_screen=True)
        self.run_visit(visit)
        # A blank page for https://check.torproject.org/ amounts to ~4.8KB.
        # A real screen capture on the other hand, is ~57KB. If the capture
        # is not blank it should be at least greater than 30KB.
        self.assertGreater(os.path.getsize(self.screenshot_path), 30000)


    def run_visit(self, visit):
        visit.get()
        self.check_expected_visit_dirs_and_files(visit)

    def setUp(self):
        self.site_num = 0
        self.batch_num = 0
        self.instance_num = 0

    def tearDown(self):
        shutil.rmtree(self.crawl_dir)

    @classmethod
    def tearDownClass(cls):
        # cls.tor_process.kill()
        cls.tor_controller.kill_tor_proc()

if __name__ == "__main__":
    unittest.main()
