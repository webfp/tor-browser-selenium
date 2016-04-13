import tempfile
import unittest
from os.path import join
import tbselenium.utils as ut
from time import sleep


class UtilsTest(unittest.TestCase):

    def test_writing_bytes_should_change_dir_mod_time(self):
        temp_dir = tempfile.mkdtemp()
        last_mod_time_before = ut.get_last_modified_of_dir(temp_dir)
        temp_file = join(temp_dir, 'temp_file')
        sleep(0.1)
        with open(temp_file, 'a') as f:
            f.write('\0')
        last_mod_time_after = ut.get_last_modified_of_dir(temp_dir)
        self.assertNotEqual(last_mod_time_before, last_mod_time_after)

if __name__ == "__main__":
    unittest.main()
