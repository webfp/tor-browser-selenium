import os
from os.path import dirname, realpath, join, basename, isdir
import sys
import unittest
sys.path.append(dirname(dirname(realpath(__file__))))
import common as cm


class Test(unittest.TestCase):

    def test_get_tbb_major_version(self):
        ver_dict = {"2.3.25-15": "2",
                    "3.5": "3",
                    "4.0.8": "4",
                    "10.0.8": "10"
                    }
        for version, major_v in ver_dict.iteritems():
            self.assert_(cm.get_tbb_major_version(version) == major_v)

    def test_get_tbb_dirname(self):
        self.assert_(cm.get_tbb_dirname("2.3.25-16") ==
                     "tor-browser-linux%s-2.3.25-16_en-US" % cm.arch)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5) ==
                     "tor-browser-linux%s-3.5_en-US" % cm.arch)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5, "linux") ==
                     "tor-browser-linux%s-3.5_en-US" % cm.arch)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5, lang="en-US") ==
                     "tor-browser-linux%s-3.5_en-US" % cm.arch)

    def assert_is_executable(self, bin_path):
        return self.assertTrue(os.access(bin_path, os.EX_OK))

    def test_get_tb_bin_path(self):
        tb_bin_path = cm.get_tb_bin_path(cm.TEST_TBB_DIR)
        self.assertEqual("firefox", basename(tb_bin_path))
        self.assert_is_executable(tb_bin_path)

    def test_get_tbb_profile_path(self):
        tbb_prof_path = cm.get_tbb_profile_path(cm.TEST_TBB_DIR)
        self.assertIn("profile", basename(tbb_prof_path))
        self.assertTrue(isdir(tbb_prof_path))
        self.assertTrue(isdir(join(tbb_prof_path, "extensions")))
        self.assertTrue(isdir(join(tbb_prof_path, "preferences")))

    def test_get_tbb_data_dir_path(self):
        ver_str = "2.3.25-16"
        tor_data_path_v2_3_25_16 = cm.get_tor_data_path(ver_str)
        self.assert_(ver_str in tor_data_path_v2_3_25_16)
        self.assert_(join('Data', 'Tor') in
                     tor_data_path_v2_3_25_16)
        self.assert_(cm.TBB_BASE_DIR in tor_data_path_v2_3_25_16)
        self.assert_(cm.get_tbb_dirname(ver_str) in
                     tor_data_path_v2_3_25_16)

        tor_data_path_v3_5 = cm.get_tor_data_path(cm.TBB_V_3_5)
        self.assert_(cm.TBB_V_3_5 in tor_data_path_v3_5)
        self.assert_(join('Data', 'Tor') in
                     tor_data_path_v3_5)
        self.assert_(cm.TBB_BASE_DIR in tor_data_path_v3_5)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5) in
                     tor_data_path_v3_5)

        tor_data_path_v4_0_8 = cm.get_tor_data_path(cm.TBB_V_4_0_8)
        self.assert_(cm.TBB_V_4_0_8 in tor_data_path_v4_0_8)
        self.assert_(join('Browser', 'TorBrowser', 'Data', 'Tor') in
                     tor_data_path_v4_0_8)
        self.assert_(cm.TBB_BASE_DIR in tor_data_path_v4_0_8)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_4_0_8) in
                     tor_data_path_v4_0_8)

    def test_get_tor_bin_path(self):
        tor_bin_path = cm.get_tor_bin_path(cm.TEST_TBB_DIR)
        self.assertEqual("tor", basename(tor_bin_path))
        self.assert_is_executable(tor_bin_path)


if __name__ == "__main__":
    unittest.main()
