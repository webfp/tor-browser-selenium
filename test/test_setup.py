import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import setup as se
import common as cm
arch = cm.arch
machine = cm.machine
from shutil import rmtree


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_url_tbb_ver(self):
        wang_and_goldberg_url = "https://archive.torproject.org/tor-package-archive/torbrowser/linux/tor-browser-gnu-linux-%s-2.4.7-alpha-1-dev-en-US.tar.gz" % machine  # noqa
        self.assertEqual(se.get_url_by_tbb_ver(cm.TBB_WANG_AND_GOLDBERG),
                         wang_and_goldberg_url)

        tbb_3_5_url = "https://archive.torproject.org/tor-package-archive/torbrowser/3.5/tor-browser-linux%s-3.5_en-US.tar.xz" % arch  # noqa
        self.assertEqual(se.get_url_by_tbb_ver(cm.TBB_V_3_5),
                         tbb_3_5_url)
        tbb_4_0_8_url = "https://archive.torproject.org/tor-package-archive/torbrowser/4.0.8/tor-browser-linux%s-4.0.8_en-US.tar.xz" % arch  # noqa
        self.assertEqual(se.get_url_by_tbb_ver(cm.TBB_V_4_0_8),
                         tbb_4_0_8_url)

    def test_get_tbb_filename(self):
        tbb_2_4_7A1 = "tor-browser-gnu-linux-%s-2.4.7-alpha-1-dev-en-US.tar.gz"\
            % machine
        self.assertEqual(se.get_tbb_filename(cm.TBB_WANG_AND_GOLDBERG),
                         tbb_2_4_7A1)
        self.assertEqual(se.get_tbb_filename(cm.TBB_V_3_5),
                         "tor-browser-linux%s-3.5_en-US.tar.xz" % arch)
        self.assertEqual(se.get_tbb_filename(cm.TBB_V_4_0_8),
                         "tor-browser-linux%s-4.0.8_en-US.tar.xz" % arch)

    def test_download_tbb_tarball(self):
        try:
            tbb_4_0_8_path = se.download_tbb_tarball(cm.TBB_V_4_0_8,
                                                     dl_dir=cm.TEST_FILES_DIR)
        except cm.TBBTarballVerificationError as e:
            self.fail(e.message)
        os.path.isfile(tbb_4_0_8_path)
        tbb_4_0_8_path.endswith("tar.xz")
        sha_sum_path = "%s.%s" % (tbb_4_0_8_path, "sha256sums.txt")
        sha_sum_sig_path = "%s%s" % (sha_sum_path, ".asc")
        os.remove(tbb_4_0_8_path)
        os.remove(sha_sum_sig_path)
        os.remove(sha_sum_path)
        rmtree(tbb_4_0_8_path.split(".tar")[0])

    def test_get_recommended_tbb_version(self):
        rec_ver = se.get_recommended_tbb_version()
        self.assertGreaterEqual(rec_ver.split('.')[0], 4)

    def test_import_tbb_signing_keys(self):
        try:
            se.import_tbb_signing_keys()
        except cm.TBBSigningKeyImportError as e:
            self.fail(e.message)

    def test_import_gpg_key(self):
        self.assertFalse(se.import_gpg_key("0xNONHEXADECIMAL"))

    def test_verify_tbb_signature(self):
        GOOD_SIG = "tor-browser-linux64-4.0.99_en-US.tar.xz.sha256sums.txt.asc"
        BAD_SIG = "bad_sig_tor-browser-linux64-4.0.99_en-US.tar.xz.sha256sums.txt.asc"  # noqa
        self.assertTrue(se.verify_tbb_sig(os.path.join(cm.TEST_FILES_DIR, GOOD_SIG)))  # noqa
        self.assertFalse(se.verify_tbb_sig(os.path.join(cm.TEST_FILES_DIR, BAD_SIG)))  # noqa

if __name__ == "__main__":
    unittest.main()
