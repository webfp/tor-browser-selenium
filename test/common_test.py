from os.path import dirname, realpath, join
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

    def test_get_tb_bin_path(self):
        ver_str = "2.3.25-16"
        tb_bin_path_v2_3_25_16 = cm.get_tb_bin_path(ver_str)
        self.assert_(ver_str in tb_bin_path_v2_3_25_16)
        self.assert_(join('App', 'Firefox', 'firefox') in
                     tb_bin_path_v2_3_25_16)

        tb_bin_path_v3_5 = cm.get_tb_bin_path(cm.TBB_V_3_5)
        self.assert_(cm.TBB_V_3_5 in tb_bin_path_v3_5)
        self.assert_(join('Browser', 'firefox') in tb_bin_path_v3_5)

        tb_bin_path_V_4_0_8 = cm.get_tb_bin_path(cm.TBB_V_4_0_8)
        self.assert_(cm.TBB_V_4_0_8 in tb_bin_path_V_4_0_8)
        self.assert_(join('Browser', 'firefox') in tb_bin_path_V_4_0_8)

        self.assert_(cm.TBB_BASE_DIR in tb_bin_path_v2_3_25_16)
        self.assert_(cm.TBB_BASE_DIR in tb_bin_path_v3_5)
        self.assert_(cm.TBB_BASE_DIR in tb_bin_path_V_4_0_8)

    def test_get_tbb_profile_path(self):
        ver_str = "2.3.25-16"
        tbb_prof_path_v2_3_25_16 = cm.get_tbb_profile_path(ver_str)
        self.assert_(cm.TBB_V2_PROFILE_PATH in tbb_prof_path_v2_3_25_16)
        self.assert_(cm.get_tbb_dirname(ver_str) in
                     tbb_prof_path_v2_3_25_16)
        self.assert_(cm.TBB_BASE_DIR in tbb_prof_path_v2_3_25_16)

        tbb_prof_path_v3_5 = cm.get_tbb_profile_path(cm.TBB_V_3_5)
        self.assert_(cm.TBB_V3_PROFILE_PATH in tbb_prof_path_v3_5)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5) in
                     tbb_prof_path_v3_5)
        self.assert_(cm.TBB_BASE_DIR in tbb_prof_path_v3_5)

        tbb_prof_path_v4_0_8 = cm.get_tbb_profile_path(cm.TBB_V_4_0_8)
        self.assert_(cm.TBB_V3_PROFILE_PATH in tbb_prof_path_v4_0_8)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_4_0_8) in
                     tbb_prof_path_v4_0_8)
        self.assert_(cm.TBB_BASE_DIR in tbb_prof_path_v4_0_8)

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
        ver_str = "2.3.25-16"
        tor_bin_path_v2_3_25_16 = cm.get_tor_bin_path(ver_str)
        self.assert_(cm.TBB_BASE_DIR in tor_bin_path_v2_3_25_16)
        self.assert_(cm.TOR_V2_BINARY_PATH in tor_bin_path_v2_3_25_16)
        self.assert_(cm.get_tbb_dirname(ver_str) in
                     tor_bin_path_v2_3_25_16)

        tor_bin_path_v3_5 = cm.get_tor_bin_path(cm.TBB_V_3_5)
        self.assert_(cm.TBB_BASE_DIR in tor_bin_path_v3_5)
        self.assert_(cm.TOR_V3_BINARY_PATH in tor_bin_path_v3_5)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_3_5) in
                     tor_bin_path_v3_5)

        tor_bin_path_v4_0_8 = cm.get_tor_bin_path(cm.TBB_V_4_0_8)
        self.assert_(cm.TBB_BASE_DIR in tor_bin_path_v4_0_8)
        self.assert_(cm.TOR_V4_BINARY_PATH in tor_bin_path_v4_0_8)
        self.assert_(cm.get_tbb_dirname(cm.TBB_V_4_0_8) in
                     tor_bin_path_v4_0_8)

if __name__ == "__main__":
    unittest.main()
