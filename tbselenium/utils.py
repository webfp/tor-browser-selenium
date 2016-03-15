import distutils.dir_util as du
from os import walk, makedirs
from os.path import join, exists
from time import strftime


def get_hash_of_directory(path):
    """Return md5 hash of the directory pointed by path."""
    from hashlib import md5
    m = md5()
    for root, _, files in walk(path):
        for f in files:
            full_path = join(root, f)
            for line in open(full_path).readlines():
                m.update(line)
    return m.digest()


def create_dir(dir_path):
    """Create a directory if it doesn't exist."""
    if not exists(dir_path):
        makedirs(dir_path)
    return dir_path


def append_timestamp(_str=''):
    """Append a timestamp to a string and return it."""
    return _str + strftime('%y%m%d_%H%M%S')


def clone_dir_with_timestap(dir_path):
    """Copy a folder in the same directory and append a timestamp."""
    new_dir = create_dir(append_timestamp(dir_path))
    du.copy_tree(dir_path, new_dir)
    return new_dir
