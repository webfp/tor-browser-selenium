import os
import sys
import unittest
from time import sleep
import commands as cmds
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import utils as ut
import common as cm
from shutil import rmtree
from tld import get_tld


class UtilsTest(unittest.TestCase):

    def test_get_filename_from_url(self):
        filename = ut.get_filename_from_url("http://google.com", 0)
        self.assertEqual("0-google.com", filename)
        filename = ut.get_filename_from_url("https://yahoo.com", 99)
        self.assertEqual("99-yahoo.com", filename)
        filename = ut.get_filename_from_url("https://123abc.com/somepath", 999)
        self.assertEqual("999-123abc.com-somepath", filename)
        filename = ut.get_filename_from_url(
            "https://123abc.com/somepath/", 123)
        self.assertEqual("123-123abc.com-somepath-", filename)
        filename = ut.get_filename_from_url(
            "https://123abc.com/somepath/q=query&q2=q2", 234)
        self.assertEqual("234-123abc.com-somepath-q-query-q2-q2", filename)

    def test_timeout(self):
        ut.timeout(1)
        try:
            sleep(1.1)
        except ut.TimeExceededError:
            pass  # this is what we want
        else:
            self.fail("Cannot set timeout")

    def test_cancel_timeout(self):
        ut.timeout(1)
        ut.cancel_timeout()
        try:
            sleep(1.1)
        except ut.TimeExceededError:
            self.fail("Cannot cancel timeout")

    def test_pack_crawl_data(self):
        self.assertTrue(ut.pack_crawl_data(cm.DUMMY_TEST_DIR))
        self.assertTrue(os.path.isfile(cm.DUMMY_TEST_DIR_TARGZIPPED))

        cmd = 'file "%s"' % cm.DUMMY_TEST_DIR_TARGZIPPED  # linux file command
        status, cmd_out = cmds.getstatusoutput(cmd)
        if not status:  # command executed successfully
            if 'gzip compressed data' not in cmd_out:
                self.fail("Cannot confirm file type")

        self.failIf(ut.is_targz_archive_corrupt(cm.DUMMY_TEST_DIR_TARGZIPPED))
        os.remove(cm.DUMMY_TEST_DIR_TARGZIPPED)

    def test_get_public_suffix(self):
        urls = ('http://www.foo.org',
                'https://www.foo.org',
                'http://www.subdomain.foo.org',
                'http://www.subdomain.foo.org:80/subfolder',
                'https://www.subdomain.foo.org:80/subfolder?p1=4545&p2=54545',
                'https://www.subdomain.foo.org:80/subfolder/baefasd==/65')
        for pub_suf_test_url in urls:
            self.assertEqual(get_tld(pub_suf_test_url),
                             "foo.org")

    def test_extract_archive(self):
        ut.extract_tbb_tarball(cm.TBB_TEST_TARBALL)
        self.assertTrue(os.path.isdir(cm.TBB_TEST_TARBALL_EXTRACTED))
        self.assertTrue(os.path.isfile(
            os.path.join(cm.TBB_TEST_TARBALL_EXTRACTED, "dummy.txt")))
        rmtree(cm.TBB_TEST_TARBALL_EXTRACTED)

if __name__ == "__main__":
    unittest.main()
