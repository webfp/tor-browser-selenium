import tempfile
import unittest
from os import makedirs, utime
from os.path import isdir, join
from shutil import rmtree

from tld import get_tld

import tbselenium.utils as ut


class TestInTemporaryFolder(object):
    test_dir = None

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        if isdir(cls.test_dir):
            rmtree(cls.test_dir)


class HashDirTest(TestInTemporaryFolder, unittest.TestCase):
    def setUp(self):
        self.test_folder_path = join(self.test_dir, 'test_folder')
        makedirs(self.test_folder_path)

    def tearDown(self):
        if isdir(self.test_folder_path):
            rmtree(self.test_folder_path)

    def test_hashes_of_two_empty_folders_are_the_equal(self):
        """Even though folders have different paths."""
        second_folder_path = join(self.test_dir, "dir1")
        makedirs(second_folder_path)
        hash_dir1 = ut.get_hash_of_directory(self.test_folder_path)
        hash_dir2 = ut.get_hash_of_directory(second_folder_path)
        self.assertEqual(hash_dir1, hash_dir2)

    def test_new_empty_file_does_not_alter_hash(self):
        """Test if after creating a new empty file the hash is the same."""
        hash_before = ut.get_hash_of_directory(self.test_folder_path)
        temp_file = join(self.test_folder_path, 'temp_file')
        with open(temp_file, 'a'):
            utime(temp_file, None)
        hash_after = ut.get_hash_of_directory(self.test_folder_path)
        self.assertEqual(hash_before, hash_after)

    def test_after_writing_bytes_changes_hash(self):
        hash_before = ut.get_hash_of_directory(self.test_folder_path)
        temp_file = join(self.test_folder_path, 'temp_file')
        with open(temp_file, 'a') as f:
            f.write('\0')
        hash_after = ut.get_hash_of_directory(self.test_folder_path)
        self.assertNotEqual(hash_before, hash_after)


class CreateDirTest(TestInTemporaryFolder, unittest.TestCase):
    def test_directory_already_exists(self):
        test_folder_path = join(self.test_dir, 'test_folder')
        makedirs(test_folder_path)
        try:
            ut.create_dir(test_folder_path)
        except:
            self.fail("Should not raise exception.")
        rmtree(test_folder_path)

    def test_directory_does_not_exist(self):
        test_folder_path = join(self.test_dir, 'test_folder')
        ut.create_dir(test_folder_path)


class TLDTest(unittest.TestCase):
    """Make sure we get the right domain for all the edge cases."""

    def test_get_public_suffix(self):
        urls = ('http://www.foo.org',
                'https://www.foo.org',
                'http://www.subdomain.foo.org',
                'http://www.subdomain.foo.org:80/subfolder',
                'https://www.subdomain.foo.org:80/subfolder?p1=4545&p2=54545',
                'https://www.subdomain.foo.org:80/subfolder/baefasd==/65')
        for pub_suf_test_url in urls:
            self.assertEqual(get_tld(pub_suf_test_url), "foo.org")


if __name__ == "__main__":
    unittest.main()
