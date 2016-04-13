import tempfile
import unittest
from os import makedirs
from os.path import join
import tbselenium.utils as ut


class UtilsTest(unittest.TestCase):

    def test_hashes_of_empty_folders_should_be_equal(self):
        """Even though folders have different paths."""
        temp_dir = tempfile.mkdtemp()
        dir1_path = join(temp_dir, "dir1")
        makedirs(dir1_path)
        dir2_path = join(temp_dir, "dir2")
        makedirs(dir2_path)
        dir1_hash = ut.get_hash_of_directory(dir1_path)
        dir2_hash = ut.get_hash_of_directory(dir2_path)
        self.assertEqual(dir1_hash, dir2_hash)

    def test_writing_bytes_should_change_dir_hash(self):
        temp_dir = tempfile.mkdtemp()
        hash_before = ut.get_hash_of_directory(temp_dir)
        temp_file = join(temp_dir, 'temp_file')
        with open(temp_file, 'a') as f:
            f.write('\0')
        hash_after = ut.get_hash_of_directory(temp_dir)
        self.assertNotEqual(hash_before, hash_after)

if __name__ == "__main__":
    unittest.main()
